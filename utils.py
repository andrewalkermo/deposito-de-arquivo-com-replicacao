import os
import enums
import socket
import hashlib

from uuid import uuid4, UUID


def check_port(port: int) -> bool:
    """
    Verifica se a porta está em uso.

    Args:
        port:

    Returns:

    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('', port))
        s.close()
        return True
    except socket.error:
        s.close()
        return False


def generate_uuid():
    return str(uuid4())


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def enviar_arquivo_por_socket(socket_destinatario, caminho_arquivo: str, tamanho_arquivo: int, tamanho_fatia: int):
    """
    Envia um arquivo por socket.
    Args:
        socket_destinatario:
        caminho_arquivo: str
        tamanho_arquivo: int
        tamanho_fatia: int
    """
    partes = int(tamanho_arquivo / tamanho_fatia)
    resto = tamanho_arquivo - (partes * tamanho_fatia)
    print('partes: {}'.format(partes))
    print('resto: {}'.format(resto))

    if resto > 0:
        partes += 1

    with open(caminho_arquivo, 'rb') as f:
        for i in range(partes):
            if i == partes - 1:
                parte = f.read(resto)
            else:
                parte = f.read(tamanho_fatia)
            socket_destinatario.send(parte)

    resultado = socket_destinatario.recv(tamanho_fatia).decode()
    if resultado == enums.Retorno.OK.value:
        print('Arquivo enviado com sucesso')
    else:
        print('Erro ao enviar arquivo')


def receber_arquivo_por_socket(
        socket_origem,
        caminho_arquivo: str,
        hash_arquivo: str,
        tamanho_arquivo: int,
        tamanho_fatia: int
):
    """
    Recebe um arquivo por socket.
    Args:
        socket_origem:
        caminho_arquivo: str
        hash_arquivo: str
        tamanho_arquivo: int
        tamanho_fatia: int
    """

    sha256_hash = hashlib.sha256()
    arquivo_bytes = open(caminho_arquivo, 'wb')
    partes = int(tamanho_arquivo / tamanho_fatia)
    resto = tamanho_arquivo - (partes * tamanho_fatia)

    if resto > 0:
        partes += 1

    for i in range(partes):
        if i == partes - 1:
            parte = socket_origem.recv(resto)
        else:
            parte = socket_origem.recv(tamanho_fatia)

        arquivo_bytes.write(parte)
        sha256_hash.update(parte)

    arquivo_bytes.close()

    if sha256_hash.hexdigest() == hash_arquivo:
        print('Arquivo recebido com sucesso!')
        socket_origem.send(enums.Retorno.OK.value.encode())
    else:
        socket_origem.send(enums.Retorno.ERRO.value.encode())
        print('Erro ao receber arquivo!')
        os.remove(caminho_arquivo)
