import sys
import signal
import socket
import hashlib
import protocolo

from enums import *
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
        return self.socket.recv(settings.get('geral.tamanho_fatia')).decode()

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

        arquivo_bytes = open(arquivo, 'rb').read()
        arquivo_nome = arquivo.split('/')[-1]
        arquivo_tamanho = len(arquivo_bytes)

        sha256_hash = hashlib.sha256()
        with open(arquivo, 'rb') as f:
            for byte_block in iter(lambda: f.read(settings.get('geral.tamanho_fatia')), b''):
                sha256_hash.update(byte_block)

        arquivo_hash = sha256_hash.hexdigest()

        solicitacao = protocolo.encapsular_solicitacao_deposito_arquivo(
            id_cliente=self.id,
            qtd_replicas=replicas,
            nome_arquivo=arquivo_nome,
            hash_arquivo=arquivo_hash,
            tamanho_arquivo=arquivo_tamanho
        )
        self.send(solicitacao)

        partes = int(arquivo_tamanho / settings.get('geral.tamanho_fatia'))
        resto = arquivo_tamanho % settings.get('geral.tamanho_fatia')
        if resto > 0:
            partes += 1

        for i in range(partes):
            if i == partes - 1:
                parte = arquivo_bytes[i * settings.get('geral.tamanho_fatia'):i * settings.get('geral.tamanho_fatia') + resto]
            else:
                parte = arquivo_bytes[i * settings.get('geral.tamanho_fatia'):i * settings.get('geral.tamanho_fatia') + settings.get('geral.tamanho_fatia')]
            self.send(parte)
        resultado = self.receive()
        if resultado == Retorno.OK.value:
            print('Arquivo depositado com sucesso')
        else:
            print('Erro ao depositar arquivo')


    def recuperar_arquivo(self):
        arquivo = str(input('Digite nome do arquivo: '))
        self.send(arquivo)
        return self.receive()


def signal_handler(client):
    print('Encerrando...')
    client.close()
    exit()


def main():
    args = sys.argv

    host = args[1] if len(args) > 1 else str(input('Digite o host: '))
    port = int(args[2]) if len(args) > 2 else int(input('Digite a porta: '))

    id_antigo = str(input('Digite o id, pode deixar em branco para criar uma nova sessão: '))
    client = Client(id_antigo, host, port)
    client.connect()

    novo_id = str(client.receive())
    if id_antigo == '':
        client.id = novo_id
        print('Seu id: {}'.format(novo_id))
        print('Guarde o id para futuras sessões')

    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(client))

    comandos = {
        '0': Comando.ENCERRAR_CONEXAO.value,
        '1': Comando.DEPOSITAR_ARQUIVO.value,
        '2': Comando.RECUPERAR_ARQUIVO.value,
    }

    while True:
        print('0 - Encerrar conexão\n1 - Depositar arquivo\n2 - Recuperar arquivo')
        comando = str(input('Digite o comando: '))
        print(comandos[comando])
        if comando in comandos:
            if comandos[comando] == Comando.ENCERRAR_CONEXAO.value:
                break
            if comandos[comando] == Comando.DEPOSITAR_ARQUIVO.value:
                client.depositar_arquivo()
            if comandos[comando] == Comando.RECUPERAR_ARQUIVO.value:
                print(client.recuperar_arquivo())
        else:
            print('Comando inválido')

    client.close()


if __name__ == '__main__':
    main()
    exit()
