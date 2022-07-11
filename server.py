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
        print('Comando recebido: {}'.format(comando))
        if comando == Comando.DEPOSITAR_ARQUIVO.value:
            self.processar_depositar_arquivo(client_socket)
        elif comando == Comando.RECUPERAR_ARQUIVO.value:
            self.processar_recuperar_arquivo(client_socket)
        elif comando == Comando.ENCERRAR_CONEXAO.value:
            client_socket.shutdown(2)
            client_socket.close()
            self.clients.remove(client_socket)
            print('Client disconnected')

    def processar_depositar_arquivo(self, client_socket):
        """
        Deposita um arquivo no servidor.
        Args:
            client_socket:
        """
        client_socket.send('1'.encode())

        solicitacao = protocolo.ClienteSolicitacaoDepositarArquivo.desencapsular(
            client_socket.recv(settings.get('geral.tamanho_fatia')).decode()
        )

        pasta = os.path.join(settings.get('server.pasta_deposito'), solicitacao.id_cliente)
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        arquivo_nome = solicitacao.nome_arquivo
        arquivo_tamanho = int(solicitacao.tamanho_arquivo)

        nome_arquivo_deposito = "{}.{}".format(solicitacao.hash_arquivo, arquivo_nome)
        print('Nome do arquivo a ser depositado: {}'.format(nome_arquivo_deposito))
        caminho_completo = os.path.join(pasta, nome_arquivo_deposito)

        utils.receber_arquivo_por_socket(
            socket_origem=client_socket,
            caminho_arquivo=caminho_completo,
            tamanho_arquivo=arquivo_tamanho,
            hash_arquivo=solicitacao.hash_arquivo,
            tamanho_fatia=settings.get('geral.tamanho_fatia')
        )

    def processar_recuperar_arquivo(self, client_socket):
        """
        Recupera um arquivo do servidor.
        Args:
            client_socket:
        """
        solicitacao = protocolo.ClienteSolicitacaoRecuperarArquivo.desencapsular(
            client_socket.recv(settings.get('geral.tamanho_fatia')).decode()
        )
        pasta = os.path.join(settings.get('server.pasta_deposito'), solicitacao.id_cliente)
        if not os.path.exists(pasta):
            client_socket.send(enums.Retorno.ERRO.value.encode())
            print('Erro ao recuperar arquivo: pasta não encontrada')
            return

        lista_de_arquivos = os.listdir(pasta)

        arquivos_na_pasta_do_cliente = [arquivo.split('.', 1)[1] for arquivo in lista_de_arquivos]
        hashs_arquivos_na_pasta_do_cliente = [arquivo.split('.', 1)[0] for arquivo in lista_de_arquivos]
        print('Arquivos na pasta do cliente: {}'.format(arquivos_na_pasta_do_cliente))
        if solicitacao.nome_arquivo not in arquivos_na_pasta_do_cliente:
            client_socket.send(enums.Retorno.ERRO.value.encode())
            print('Erro ao recuperar arquivo: arquivo não encontrado')
            return

        indice_arquivo = arquivos_na_pasta_do_cliente.index(solicitacao.nome_arquivo)
        hash_arquivo = hashs_arquivos_na_pasta_do_cliente[indice_arquivo]

        caminho_completo = os.path.join(pasta, "{}.{}".format(hash_arquivo, solicitacao.nome_arquivo))
        arquivo_tamanho = os.path.getsize(caminho_completo)

        client_socket.send(protocolo.ServidorSolicitaEnvioArquivoRecuperadoParaCliente(
            hash_arquivo=hash_arquivo,
            tamanho_arquivo=arquivo_tamanho
        ).encapsular().encode())

        utils.enviar_arquivo_por_socket(
            socket_destinatario=client_socket,
            caminho_arquivo=caminho_completo,
            tamanho_arquivo=arquivo_tamanho,
            tamanho_fatia=settings.get('geral.tamanho_fatia')
        )
        resposta = client_socket.recv(settings.get('geral.tamanho_fatia')).decode()
        if resposta == enums.Retorno.OK.value:
            print('Arquivo enviado com sucesso')
        else:
            print('Erro ao enviar arquivo')


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
