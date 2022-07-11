from deposito_de_arquivo_com_replicacao.server_client import ServerClient


class Mirror(ServerClient):
    pass


def main():
    mirror = Mirror.create()


if __name__ == '__main__':
    main()
    exit()
