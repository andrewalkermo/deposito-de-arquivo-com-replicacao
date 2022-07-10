from enum import Enum


class Comando(Enum):
    """
    Enum com os comandos que podem ser enviados para o servidor.
    """
    DEPOSITAR_ARQUIVO = 'depositar_arquivo'
    RECUPERAR_ARQUIVO = 'recuperar_arquivo'
    ENCERRAR_CONEXAO = 'encerrar_conexao'


class Retorno(Enum):
    """
    Enum com os retornos que podem ser enviados para o cliente.
    """
    OK = '1'
    ERRO = '0'
