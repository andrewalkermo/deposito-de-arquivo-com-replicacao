import os
import sys
import signal
import socket
import select
import threading
from re import match

from deposito_de_arquivo_com_replicacao.config import settings
from deposito_de_arquivo_com_replicacao import enums, protocolo, utils


class Server:
    def __init__(self, port):
        self.port = port
        self.socket = None
        self.clients = []
        self.mirrors = []

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(1)
        print('Servidor iniciado na porta {}'.format(self.port))

    def accept(self):
        server_client_socket, client_address = self.socket.accept()
        self.clients.append(server_client_socket)
        print('Novo cliente conectado {}'.format(client_address))
        server_thread = threading.Thread(target=self.handle_server_client, args=(server_client_socket,))
        server_thread.start()

    def close(self):
        for server_client_socket in self.clients:
            server_client_socket.shutdown(2)
            server_client_socket.close()
        for mirror in self.mirrors:
            mirror['socket'].shutdown(2)
            mirror['socket'].close()
        self.socket.close()

    def receice(self, server_client_socket):
        pass

    def handle_server_client(self, server_client_socket):
        while True:
            try:
                ready_to_read, ready_to_write, in_error = select.select([server_client_socket, ], [server_client_socket, ], [], 5)
            except select.error:
                server_client_socket.shutdown(2)
                server_client_socket.close()
                print('erro de conexão')
                break
            if len(ready_to_read) > 0:
                message = server_client_socket.recv(settings.get('geral.tamanho_buffer_padrao')).decode()
                if message:
                    self.processa_comando_recebido(server_client_socket, message)
                else:
                    break
            if len(ready_to_write) > 0:
                pass
            if len(in_error) > 0:
                break

        # find in list of mirros and remove it
        for mirror in self.mirrors:
            if mirror['socket'] == server_client_socket:
                self.mirrors.remove(mirror)
                print('Mirror removido. Disponíveis: {}'.format(len(self.mirrors)))
                break

        server_client_socket.close()
        self.clients.remove(server_client_socket)
        print('Client disconnected')

    def processa_comando_recebido(self, server_client_socket, comando: str):
        """
        Processa o comando do cliente.
        Args:
            server_client_socket:
            comando:
        """
        print('Comando recebido: {}'.format(comando))
        if comando == enums.Comando.DEPOSITAR_ARQUIVO.value:
            self.processar_depositar_arquivo(server_client_socket)
        elif comando == enums.Comando.RECUPERAR_ARQUIVO.value:
            self.processar_recuperar_arquivo(server_client_socket)
        elif match(protocolo.SolicitacaoRegistrarMirror.pattern, comando):
            self.processar_registrar_mirror(server_client_socket, comando)

        elif comando == enums.Comando.ENCERRAR_CONEXAO.value:
            server_client_socket.shutdown(2)
            server_client_socket.close()
            self.clients.remove(server_client_socket)
            print('Client disconnected')
        else:
            # find in list of mirrors or clients
            for mirror in self.mirrors:
                if mirror['socket'] == server_client_socket:
                    print('Mirror: {}'.format(mirror['id_mirror']))
                    break
            for client_socket in self.clients:
                if client_socket == server_client_socket:
                    print('Cliente recebido')
                    break

    def processar_depositar_arquivo(self, server_client_socket):
        """
        Deposita um arquivo no servidor.
        Args:
            server_client_socket:
        """
        server_client_socket.send(str(len(self.mirrors)).encode())

        solicitacao = protocolo.ClienteSolicitacaoDepositarArquivo.desencapsular(
            server_client_socket.recv(settings.get('geral.tamanho_buffer_padrao')).decode()
        )

        pasta = os.path.join(settings.get('server.pasta_deposito'), solicitacao.id_cliente)
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        arquivo_nome = solicitacao.nome_arquivo
        arquivo_tamanho = int(solicitacao.tamanho_arquivo)

        nome_arquivo_deposito = "{}.{}".format(solicitacao.hash_arquivo, arquivo_nome)
        print('Nome do arquivo a ser depositado: {}'.format(nome_arquivo_deposito))
        caminho_completo = os.path.join(pasta, nome_arquivo_deposito)

        resultado = utils.receber_arquivo_por_socket(
            socket_origem=server_client_socket,
            caminho_arquivo=caminho_completo,
            tamanho_arquivo=arquivo_tamanho,
            hash_arquivo=solicitacao.hash_arquivo
        )
        if resultado:
            # envia para as replicas em threads
            threading.Thread(target=self.enviar_arquivo_para_replicas, kwargs=({
                'qtd_replicas': solicitacao.qtd_replicas,
                'caminho_arquivo': caminho_completo,
                'hash_arquivo': solicitacao.hash_arquivo,
                'nome_arquivo': arquivo_nome,
                'tamanho_arquivo': arquivo_tamanho,
                'id_cliente': solicitacao.id_cliente
            })).start()
            # envia replicados para o cliente

    def enviar_arquivo_para_replicas(self, qtd_replicas, nome_arquivo, caminho_arquivo, tamanho_arquivo, hash_arquivo, id_cliente):
        """
        Envia um arquivo para as replicas.
        Args:
            hash_arquivo:
            tamanho_arquivo:
            qtd_replicas:
            nome_arquivo:
            caminho_arquivo:
        """
        print('Enviando arquivo para {} replicas'.format(qtd_replicas))
        replicados = 0
        for mirror in self.mirrors:
            if replicados < int(qtd_replicas):
                replicado = self.enviar_arquivo_para_mirror(
                    mirror=mirror,
                    nome_arquivo=nome_arquivo,
                    caminho_arquivo=caminho_arquivo,
                    tamanho_arquivo=tamanho_arquivo,
                    hash_arquivo=hash_arquivo,
                    id_cliente=id_cliente
                )
                if replicado:
                    replicados += 1
        return replicados

    def enviar_arquivo_para_mirror(self, mirror, nome_arquivo, caminho_arquivo, tamanho_arquivo, hash_arquivo, id_cliente):
        """
        Envia um arquivo para um mirror.
        Args:
            id_cliente:
            hash_arquivo:
            tamanho_arquivo:
            mirror:
            nome_arquivo:
            caminho_arquivo:
        """
        print('Enviando arquivo para o mirror {}'.format(mirror['id_mirror']))
        mirror_socket = mirror['socket']
        mirror_socket.send(protocolo.ServidorsolicitarReplicarArquivo(
            id_cliente=id_cliente,
            nome_arquivo=nome_arquivo,
            tamanho_arquivo=tamanho_arquivo,
            hash_arquivo=hash_arquivo
        ).encapsular().encode())

        resultado = mirror_socket.recv(settings.get('geral.tamanho_buffer_padrao')).decode()
        if resultado == enums.Retorno.ERRO.value:
            print('Erro ao replicar arquivo para o mirror')
            return False

        return utils.enviar_arquivo_por_socket(
            socket_destinatario=mirror_socket,
            caminho_arquivo=caminho_arquivo,
            tamanho_arquivo=tamanho_arquivo
        )

    def processar_recuperar_arquivo(self, server_client_socket):
        """
        Recupera um arquivo do servidor.
        Args:
            server_client_socket:
        """
        solicitacao = protocolo.ClienteSolicitacaoRecuperarArquivo.desencapsular(
            server_client_socket.recv(settings.get('geral.tamanho_buffer_padrao')).decode()
        )
        pasta = os.path.join(settings.get('server.pasta_deposito'), solicitacao.id_cliente)
        if not os.path.exists(pasta):
            server_client_socket.send(enums.Retorno.ERRO.value.encode())
            print('Erro ao recuperar arquivo: pasta não encontrada')
            return

        lista_de_arquivos = os.listdir(pasta)

        arquivos_na_pasta_do_cliente = [arquivo.split('.', 1)[1] for arquivo in lista_de_arquivos]
        hashs_arquivos_na_pasta_do_cliente = [arquivo.split('.', 1)[0] for arquivo in lista_de_arquivos]
        print('Arquivos na pasta do cliente: {}'.format(arquivos_na_pasta_do_cliente))
        if solicitacao.nome_arquivo not in arquivos_na_pasta_do_cliente:
            server_client_socket.send(enums.Retorno.ERRO.value.encode())
            print('Erro ao recuperar arquivo: arquivo não encontrado')
            return

        indice_arquivo = arquivos_na_pasta_do_cliente.index(solicitacao.nome_arquivo)
        hash_arquivo = hashs_arquivos_na_pasta_do_cliente[indice_arquivo]

        caminho_completo = os.path.join(pasta, "{}.{}".format(hash_arquivo, solicitacao.nome_arquivo))
        arquivo_tamanho = os.path.getsize(caminho_completo)

        server_client_socket.send(protocolo.ServidorSolicitaEnvioArquivoRecuperadoParaCliente(
            hash_arquivo=hash_arquivo,
            tamanho_arquivo=arquivo_tamanho
        ).encapsular().encode())

        utils.enviar_arquivo_por_socket(
            socket_destinatario=server_client_socket,
            caminho_arquivo=caminho_completo,
            tamanho_arquivo=arquivo_tamanho
        )

    def processar_registrar_mirror(self, server_client_socket, comando: str):
        """
        Registra um mirror no servidor.
        Args:
            server_client_socket:
            comando:
        """
        solicitacao = protocolo.SolicitacaoRegistrarMirror.desencapsular(comando)
        self.mirrors.append(
            {
                'id_mirror': solicitacao.id_mirror,
                'socket': server_client_socket
            }
        )
        server_client_socket.send(enums.Retorno.OK.value.encode())
        print('Mirror {} registrado com sucesso. Total de mirrors: {}'.format(solicitacao.id_mirror, len(self.mirrors)))

    def signal_handler(self):
        print('Encerrando...')
        self.close()
        exit()

    @staticmethod
    def create(args):
        """
        Cria uma instância do servidor.
        """
        port = int(args[1]) if len(args) > 1 else int(input('Digite a porta: '))

        if not utils.check_port(port):
            print('Porta já está em uso')
            exit()

        server = Server(port)
        server.start()

        signal.signal(signal.SIGINT, lambda signum, frame: server.signal_handler())
        return server


def main(args):
    server = Server.create(args)
    print('Aguardando conexão...')
    while True:
        server.accept()


if __name__ == '__main__':
    main(sys.argv)
    exit()
