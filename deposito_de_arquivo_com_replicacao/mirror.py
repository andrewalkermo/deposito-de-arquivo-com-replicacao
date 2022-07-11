import sys

from deposito_de_arquivo_com_replicacao.server_client import ServerClient


class Mirror(ServerClient):
    pass


def main(args):
    mirror = Mirror.create(args)


if __name__ == '__main__':
    main(sys.argv)
    exit()
