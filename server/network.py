import socket

class Network():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '127.0.0.1'
        self.port = 8000
        self.addr = (self.server, self.port)

    def connect(self):
        try:
            self.client.connect(self.addr)
            data = self.client.recv(2048*9).decode()
            self.pos = data
            return data
        except:
            return False
    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048*9).decode()
        except socket.error as e:
            print(e)

    def getPos(self):
        return self.pos
