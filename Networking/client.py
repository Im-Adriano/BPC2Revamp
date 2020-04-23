import json
import multiprocessing
import socket


class Client:
    def __init__(self,
                 server_host,
                 server_port_tcp=1234,
                 server_port_udp=1234,
                 client_port_udp=8888):
        """
        Create a game server client
        """
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.settimeout(5)
        self.identifier = None
        self.server_message = []
        self.room_id = None
        self.client_udp = ("0.0.0.0", client_port_udp)
        self.parentPipe, self.childPipe = multiprocessing.Pipe()
        self.server_udp = (server_host, server_port_udp)
        self.server_tcp = (server_host, server_port_tcp)
        self.register()
        self.server_listener_class = SocketThread(self.client_udp, self.childPipe)
        self.server_listener = multiprocessing.Process(target=self.server_listener_class.run)
        self.server_listener.start()

    def cleanup(self):
        try:
            self.leave_room()
        except ConnectionResetError as e:
            pass
        self.sock_tcp.close()
        self.server_listener_class.stop()
        self.server_listener.terminate()

    def create_room(self, room_name=None):
        """
        Create a new room on server
        """
        message = json.dumps({"action": "create", "payload": room_name, "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        self.room_id = message

    def join_room(self, room_id):
        """
        Join an existing room
        """
        self.room_id = room_id
        message = json.dumps({"action": "join", "payload": room_id, "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        self.room_id = message

    def autojoin(self):
        """
        Join the first non-full room
        """
        message = json.dumps({"action": "autojoin", "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        self.room_id = message

    def leave_room(self):
        """
        Leave the current room
        """
        message = json.dumps({
            "action": "leave",
            "room_id": self.room_id,
            "identifier": self.identifier
        }).encode()
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message)
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)

    def get_rooms(self):
        """
        Get the list of remote rooms
        """
        message = json.dumps({"action": "get_rooms", "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        return message

    def send(self, message):
        """
        Send data to all players in the same room
        """
        if self.room_id == '':
            print('Connect to a room first')
        message = json.dumps({
            "action": "send",
            "payload": {"message": message},
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), self.server_udp)

    def push(self, message):
        if self.room_id == '':
            print('Connect to a room first')
        message = json.dumps({
            "action": "push",
            "payload": {"message": message},
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), self.server_udp)

    def execute(self, message):
        if self.room_id == '':
            print('Connect to a room first')
        message = json.dumps({
            "action": "execute",
            "payload": {"message": message},
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), self.server_udp)

    def register(self):
        """
        Register the client to server and get a uniq identifier
        """
        message = json.dumps({
            "action": "register",
            "payload": self.client_udp[1]
        })
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        self.identifier = message

    def parse_data(self, data):
        """
        Parse response from server
        """
        try:
            data = json.loads(data)
            if data['success'] == "True":
                return data['message']
            else:
                raise Exception(data['message'])
        except ValueError:
            print(data)

    def get_messages(self):
        """
        Get recieved messages from server
        """
        message = list()
        while self.parentPipe.poll():
            message.append(self.parentPipe.recv())
        return message


class SocketThread:
    def __init__(self, addr, pipe):
        """
        Client udp connection
        """
        self.pipe = pipe
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(addr)

    def run(self):
        """
        Get responses from server
        """
        while True:
            data, addr = self.sock.recvfrom(4096)
            self.pipe.send(data)

    def stop(self):
        """
        Stop thread
        """
        self.sock.close()
