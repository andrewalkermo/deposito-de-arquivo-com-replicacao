import socket


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

