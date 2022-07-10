import os
import sys

import enums
import utils
import signal
import socket
import select
import hashlib
import threading
import protocolo

from enums import *
from config import settings


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

    def receice(self, client_socket):
        pass

    def handle_client(self, client_socket):
        client_socket.send(utils.generate_uuid().encode())
        while True:
            try:
                ready_to_read, ready_to_write, in_error = select.select([client_socket, ], [client_socket, ], [], 1)
            except select.error:
                client_socket.shutdown(2)
                client_socket.close()
                print('erro de conexão')
                break
            if len(ready_to_read) > 0:
                message = client_socket.recv(settings.get('geral.tamanho_fatia')).decode()
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

        solicitacao = protocolo.desencapsular_solicitacao_deposito_arquivo(
            client_socket.recv(settings.get('geral.tamanho_fatia')).decode()
        )

        pasta = os.path.join(settings.get('server.pasta_deposito'), solicitacao.id_cliente)
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        arquivo_nome = solicitacao.nome_arquivo
        arquivo_tamanho = int(solicitacao.tamanho_arquivo)

        sha256_hash = hashlib.sha256()

        nome_arquivo_deposito = "{}.{}".format(solicitacao.hash_arquivo, arquivo_nome)
        print('Nome do arquivo a ser depositado: {}'.format(nome_arquivo_deposito))
        caminho_completo = os.path.join(pasta, nome_arquivo_deposito)

        arquivo_bytes = open(caminho_completo, 'wb')

        partes = int(arquivo_tamanho / settings.get('geral.tamanho_fatia'))
        resto = arquivo_tamanho % settings.get('geral.tamanho_fatia')
        if resto > 0:
            partes += 1

        for i in range(partes):
            if i == partes - 1:
                parte = client_socket.recv(resto)
            else:
                parte = client_socket.recv(settings.get('geral.tamanho_fatia'))
            sha256_hash.update(parte)
            arquivo_bytes.write(parte)
        arquivo_bytes.close()
        if sha256_hash.hexdigest() == solicitacao.hash_arquivo:
            print('Arquivo {} depositado com sucesso'.format(caminho_completo))
            client_socket.send(enums.Retorno.OK.value.encode())
        else:
            client_socket.send(enums.Retorno.ERRO.value.encode())
            print('Erro ao depositar arquivo {}'.format(caminho_completo))
            os.remove(caminho_completo)


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
