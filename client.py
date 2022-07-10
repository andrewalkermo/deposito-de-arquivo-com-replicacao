import signal
import socket
import threading


class Client:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.connected = True

    def send(self, message):
        self.socket.send(message.encode())

    def receive(self):
        return self.socket.recv(1024).decode()

    def close(self):
        self.socket.close()
        self.connected = False


def main():
    host = str(input('Digite o host: '))
    port = int(input('Digite a porta: '))
    client = Client('Cliente', host, port)
    client.connect()

    signal.signal(signal.SIGTERM, client.close)
    signal.signal(signal.SIGINT, client.close)

    while True:
        arquivo = str(input('Digite o caminho do arquivo: '))
        replicas = int(input('Digite quantas replicas: '))
        client.send(arquivo)


if __name__ == '__main__':

    main()
    exit()
