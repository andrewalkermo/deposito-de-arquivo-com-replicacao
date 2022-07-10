import socket
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

