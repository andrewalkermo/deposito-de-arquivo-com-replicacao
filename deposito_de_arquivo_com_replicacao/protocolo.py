from re import match
from abc import abstractmethod


class Protocolo:

    pattern = None

    @abstractmethod
    def encapsular(self):
        pass

    @staticmethod
    @abstractmethod
    def desencapsular(mensagem: str):
        pass


class ClienteSolicitacaoDepositarArquivo(Protocolo):

    pattern = '^id_cliente:(.*)\|qtd_replicas:(\d+)\|tamanho_arquivo:(\d+)\|hash_arquivo:(.*)\|nome_arquivo:(.*)$'

    def __init__(self, id_cliente, qtd_replicas, tamanho_arquivo, hash_arquivo, nome_arquivo):
        self.id_cliente = id_cliente
        self.qtd_replicas = qtd_replicas
        self.tamanho_arquivo = tamanho_arquivo
        self.hash_arquivo = hash_arquivo
        self.nome_arquivo = nome_arquivo

    def encapsular(self):
        return "id_cliente:{}|qtd_replicas:{}|tamanho_arquivo:{}|hash_arquivo:{}|nome_arquivo:{}".format(
            self.id_cliente, self.qtd_replicas, self.tamanho_arquivo, self.hash_arquivo, self.nome_arquivo
        )

    @staticmethod
    def desencapsular(mensagem):
        id_cliente, qtd_replicas, tamanho_arquivo, hash_arquivo, nome_arquivo = match(
            ClienteSolicitacaoDepositarArquivo.pattern,
            mensagem
        ).groups()
        return ClienteSolicitacaoDepositarArquivo(
            id_cliente=id_cliente,
            qtd_replicas=qtd_replicas,
            tamanho_arquivo=tamanho_arquivo,
            hash_arquivo=hash_arquivo,
            nome_arquivo=nome_arquivo
        )


class ClienteSolicitacaoRecuperarArquivo(Protocolo):

    pattern = '^id_cliente:(.*)\|nome_arquivo:(.*)$'

    def __init__(self, id_cliente, nome_arquivo):
        self.id_cliente = id_cliente
        self.nome_arquivo = nome_arquivo

    def encapsular(self):
        return "id_cliente:{}|nome_arquivo:{}".format(
            self.id_cliente, self.nome_arquivo
        )

    @staticmethod
    def desencapsular(mensagem):
        id_cliente, nome_arquivo = match(
            ClienteSolicitacaoRecuperarArquivo.pattern,
            mensagem
        ).groups()
        return ClienteSolicitacaoRecuperarArquivo(
            id_cliente=id_cliente,
            nome_arquivo=nome_arquivo
        )


class ServidorSolicitaEnvioArquivoRecuperadoParaCliente(Protocolo):

    pattern = '^tamanho_arquivo:(\d+)\|hash_arquivo:(.*)$'

    def __init__(self, tamanho_arquivo, hash_arquivo):
        self.tamanho_arquivo = tamanho_arquivo
        self.hash_arquivo = hash_arquivo

    def encapsular(self):
        return "tamanho_arquivo:{}|hash_arquivo:{}".format(
            self.tamanho_arquivo, self.hash_arquivo
        )

    @staticmethod
    def desencapsular(mensagem):
        tamanho_arquivo, hash_arquivo = match(
            ServidorSolicitaEnvioArquivoRecuperadoParaCliente.pattern,
            mensagem
        ).groups()
        return ServidorSolicitaEnvioArquivoRecuperadoParaCliente(
            tamanho_arquivo=tamanho_arquivo,
            hash_arquivo=hash_arquivo,
        )
