import sys
import utils
import signal
import socket
import select
import threading
import protocolo
from enums import *


class Server:
    def __init__(self, port):
        self.port = port
        self.socket = None
        self.clients = []
        self.servers = []

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(1)
        print('Servidor iniciado na porta {}'.format(self.port))

    def accept(self):
        client_socket, client_address = self.socket.accept()
        self.clients.append(client_socket)
        print('Novo cliente conectado {}'.format(client_address))
        server_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
        server_thread.start()

    def close(self):
        for client_socket in self.clients:
            client_socket.close()
        self.socket.close()

    def handle_client(self, client_socket):
        while True:
            try:
                ready_to_read, ready_to_write, in_error = select.select([client_socket, ], [client_socket, ], [], 1)
            except select.error:
                client_socket.shutdown(2)
                client_socket.close()
                print('erro de conexão')
                break
            if len(ready_to_read) > 0:
                message = client_socket.recv(1024).decode()
                if message:
                    self.processa_comando_do_cliente(client_socket, message)
            if len(ready_to_write) > 0:
                pass
            if len(in_error) > 0:
                break

        client_socket.close()
        self.clients.remove(client_socket)
        print('Client disconnected')

    def processa_comando_do_cliente(self, client_socket, comando: str):
        """
        Processa o comando do cliente.
        Args:
            client_socket:
            comando:
        """
        if comando == Comando.DEPOSITAR_ARQUIVO.value:
            self.processar_depositar_arquivo(client_socket)
        elif comando == Comando.RECUPERAR_ARQUIVO.value:
            pass
        elif comando == Comando.ENCERRAR_CONEXAO.value:
            pass

    def processar_depositar_arquivo(self, client_socket):
        """
        Deposita um arquivo no servidor.
        Args:
            client_socket:
        """
        client_socket.send('1'.encode())

        solicitacao = protocolo.desencapsular_solicitacao_deposito_arquivo(client_socket.recv(1024).decode())

        arquivo_nome = solicitacao.nome_arquivo
        arquivo_tamanho = int(solicitacao.tamanho_arquivo)

        arquivo_bytes = open(arquivo_nome, 'wb')

        partes = int(arquivo_tamanho / 1024)
        resto = arquivo_tamanho % 1024
        if resto > 0:
            partes += 1

        for i in range(partes):
            if i == partes - 1:
                parte = client_socket.recv(resto)
            else:
                parte = client_socket.recv(1024)
            arquivo_bytes.write(parte)
        arquivo_bytes.close()
        print('Arquivo {} depositado com sucesso'.format(arquivo_nome))








def signal_handler(server):
    print('Encerrando...')
    server.close()
    exit()


def main():
    args = sys.argv
    port = int(args[1]) if len(args) > 1 else int(input('Digite a porta: '))

    if not utils.check_port(port):
        print('Porta já está em uso')
        exit()

    server = Server(port)
    server.start()

    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(server))

    print('Aguardando conexão...')
    while True:
        server.accept()


if __name__ == '__main__':
    main()
    exit()
