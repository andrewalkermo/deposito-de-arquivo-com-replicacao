import socket
import threading

from enums import *


class Server:
    def __init__(self, port):
        self.port = port
        self.socket = None
        self.clients = []

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(1)
        print('Server started on port {}'.format(self.port))

    def accept(self):
        client_socket, client_address = self.socket.accept()
        self.clients.append(client_socket)
        print('Client connected from {}'.format(client_address))
        server_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
        server_thread.start()

    def close(self):
        for client_socket in self.clients:
            client_socket.close()
        self.socket.close()

    def handle_client(self, client_socket):
        while True:
            print("oi")
            message = client_socket.recv(1024).decode()
            print(message)
            if message == Comando.ENCERRAR_CONEXAO.value:
                break

        client_socket.close()
        self.clients.remove(client_socket)
        print('Client disconnected')


def main():
    port = int(input('Digite a porta desejada: '))
    server = Server(port)
    server.start()

    # executa em threads separadas
    while True:
        thread = threading.Thread(target=server.accept)
        thread.start()


if __name__ == '__main__':
    main()
    exit()
