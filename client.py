import os
import sys
import signal
import socket
import hashlib
import protocolo
import utils

from enums import *
from re import match
from config import settings


class Client:
    def __init__(self, id, ip, port):
        self.id = id
        self.ip = ip
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.connected = True

    def send(self, message):
        # check if has encode
        if isinstance(message, str):
            message = message.encode()
        self.socket.send(message)

    def receive(self):
        return self.socket.recv(settings.get('geral.tamanho_buffer_padrao')).decode()

    def close(self):
        self.socket.close()
        self.connected = False

    def depositar_arquivo(self):
        self.send(Comando.DEPOSITAR_ARQUIVO.value)
        replicas_disponiveis = int(self.receive())
        arquivo = str(input('Digite o caminho do arquivo: '))
        print('Replicas disponíveis: {}'.format(replicas_disponiveis))
        replicas = int(input('Digite quantas replicas: '))
        if replicas > replicas_disponiveis:
            print('Não há replicas disponíveis')
            return

        arquivo_nome = arquivo.split('/')[-1]
        arquivo_tamanho = os.path.getsize(arquivo)

        sha256_hash = hashlib.sha256()
        with open(arquivo, 'rb') as f:
            for byte_block in iter(lambda: f.read(settings.get('geral.tamanho_buffer_arquivo')), b''):
                sha256_hash.update(byte_block)

        arquivo_hash = sha256_hash.hexdigest()

        solicitacao = protocolo.ClienteSolicitacaoDepositarArquivo(
            id_cliente=self.id,
            qtd_replicas=replicas,
            nome_arquivo=arquivo_nome,
            hash_arquivo=arquivo_hash,
            tamanho_arquivo=arquivo_tamanho
        ).encapsular()
        self.send(solicitacao)

        utils.enviar_arquivo_por_socket(
            socket_destinatario=self.socket,
            tamanho_arquivo=arquivo_tamanho,
            tamanho_fatia=settings.get('geral.tamanho_buffer_arquivo'),
            caminho_arquivo=arquivo
        )

    def recuperar_arquivo(self):
        self.send(Comando.RECUPERAR_ARQUIVO.value)
        arquivo_nome = str(input('Digite nome do arquivo: '))

        solicitacao = protocolo.ClienteSolicitacaoRecuperarArquivo(
            id_cliente=self.id,
            nome_arquivo=arquivo_nome
        ).encapsular()
        self.send(solicitacao)

        resultado = self.receive()
        if resultado == Retorno.ERRO.value:
            print('Arquivo não encontrado')
            return
        elif match(protocolo.ServidorSolicitaEnvioArquivoRecuperadoParaCliente.pattern, resultado):
            print('Arquivo disponível')
            dados_arquivo_recuperado = protocolo.ServidorSolicitaEnvioArquivoRecuperadoParaCliente.desencapsular(
                mensagem=resultado
            )

            caminho_arquivo = os.path.join(
                settings.get('client.pasta_recuperados'),
                arquivo_nome
            )
            tamanho_arquivo = int(dados_arquivo_recuperado.tamanho_arquivo)

            utils.receber_arquivo_por_socket(
                socket_origem=self.socket,
                tamanho_arquivo=tamanho_arquivo,
                tamanho_fatia=settings.get('geral.tamanho_buffer_arquivo'),
                caminho_arquivo=caminho_arquivo,
                hash_arquivo=dados_arquivo_recuperado.hash_arquivo
            )

            print('Arquivo recuperado com sucesso')

def signal_handler(client):
    print('Encerrando...')
    client.close()
    exit()


def main():
    args = sys.argv

    host = args[1] if len(args) > 1 else str(input('Digite o host: '))
    port = int(args[2]) if len(args) > 2 else int(input('Digite a porta: '))

    client_id = str(input('Digite o id, pode deixar em branco para criar uma nova sessão: '))

    if client_id == '':
        client_id = utils.generate_uuid()
        print('Seu id: {}'.format(client_id))
        print('Guarde o id para futuras sessões')

    client = Client(client_id, host, port)
    client.connect()

    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(client))

    comandos = {
        '0': Comando.ENCERRAR_CONEXAO.value,
        '1': Comando.DEPOSITAR_ARQUIVO.value,
        '2': Comando.RECUPERAR_ARQUIVO.value,
    }

    while True:
        print('0 - Encerrar conexão\n1 - Depositar arquivo\n2 - Recuperar arquivo')
        comando = str(input('Digite o comando: '))
        if comando in comandos:
            if comandos[comando] == Comando.ENCERRAR_CONEXAO.value:
                break
            if comandos[comando] == Comando.DEPOSITAR_ARQUIVO.value:
                client.depositar_arquivo()
            if comandos[comando] == Comando.RECUPERAR_ARQUIVO.value:
                client.recuperar_arquivo()
        else:
            print('Comando inválido')

    client.close()


if __name__ == '__main__':
    main()
    exit()
