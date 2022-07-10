from re import match


class DepositarArquivo:
    def __init__(self, qtd_replicas, tamanho_arquivo, hash_arquivo, nome_arquivo):
        self.qtd_replicas = qtd_replicas
        self.tamanho_arquivo = tamanho_arquivo
        self.hash_arquivo = hash_arquivo
        self.nome_arquivo = nome_arquivo


class RecuperarArquivo:
    def __init__(self, nome_arquivo):
        self.nome_arquivo = nome_arquivo


def encapsular_solicitacao_deposito_arquivo(
        qtd_replicas: int,
        tamanho_arquivo: int,
        hash_arquivo: str,
        nome_arquivo: str
) -> str:
    """
    Encapsula a solicitação de depósito de arquivo.
    Args:
        qtd_replicas: int
        tamanho_arquivo: int
        hash_arquivo: str
        nome_arquivo: str

    Returns:
        str: solicitacao
    """
    return "{{qtd_replicas:{}|tamanho_arquivo:{}|hash_arquivo:{}|nome_arquivo:{}}}".format(
        qtd_replicas, tamanho_arquivo, hash_arquivo, nome_arquivo
    )


def encapsular_solicitacao_recuperacao_arquivo(nome_arquivo: str) -> str:
    """
    Encapsula a solicitação de recuperação de arquivo.
    Args:
        nome_arquivo: str

    Returns:
        str: solicitacao
    """
    return '{{nome_arquivo:{}}}'.format(nome_arquivo)


def desencapsular_solicitacao_deposito_arquivo(solicitacao: str) -> DepositarArquivo:
    """
    Desencapsula a solicitação de depósito de arquivo.
    Args:
        solicitacao: str

    Returns:
        DepositarArquivo
    """
    qtd_replicas, tamanho_arquivo, hash_arquivo, nome_arquivo = match(
        '^{qtd_replicas:(\d+)\|tamanho_arquivo:(\d+)\|hash_arquivo:(.*)\|nome_arquivo:(.*)}$',
        solicitacao
    ).groups()
    return DepositarArquivo(
        qtd_replicas=qtd_replicas,
        tamanho_arquivo=tamanho_arquivo,
        hash_arquivo=hash_arquivo,
        nome_arquivo=nome_arquivo
    )


def desencapsular_solicitacao_recuperacao_arquivo(solicitacao: str) -> RecuperarArquivo:
    """
    Desencapsula a solicitação de recuperação de arquivo.
    Args:
        solicitacao: str

    Returns:
        RecuperarArquivo
    """
    nome_arquivo = match('{{nome_arquivo:(.*)}}', solicitacao).group(1)
    return RecuperarArquivo(nome_arquivo)
