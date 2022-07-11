import os
import sys
import threading

from re import match

from deposito_de_arquivo_com_replicacao.config import settings
from deposito_de_arquivo_com_replicacao import utils, enums, protocolo
from deposito_de_arquivo_com_replicacao.server_client import ServerClient


class Mirror(ServerClient):
    pass

    def registrar_mirror(self):
        print('Registrando mirror {}'.format(self.id))
        self.send(
            protocolo.SolicitacaoRegistrarMirror(
                comando=enums.Comando.REGISTRAR_MIRROR.value,
                id_mirror=self.id,
            ).encapsular()
        )
        resposta = self.receive()
        if resposta == enums.Retorno.OK.value:
            print('Mirror registrado com sucesso.')
        else:
            print('Erro ao registrar mirror.')
            sys.exit(1)

    def salvar_replica(self, mensagem):
        print('Salvando replica')

        solicitacao = protocolo.ServidorsolicitarReplicarArquivo.desencapsular(mensagem)

        pasta = os.path.join(settings.get('mirror.pasta_mirror'), solicitacao.id_cliente)
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        arquivo_tamanho = int(solicitacao.tamanho_arquivo)
        nome_arquivo = "{}.{}".format(solicitacao.hash_arquivo, solicitacao.nome_arquivo)
        print('Nome do arquivo a ser replicado: {}'.format(nome_arquivo))
        caminho_completo = os.path.join(pasta, nome_arquivo)

        self.send(enums.Retorno.OK.value)
        utils.receber_arquivo_por_socket(
            socket_origem=self.socket,
            caminho_arquivo=caminho_completo,
            tamanho_arquivo=arquivo_tamanho,
            hash_arquivo=solicitacao.hash_arquivo,
            tamanho_fatia=settings.get('geral.tamanho_buffer_arquivo')
        )
        print('Arquivo replicado com sucesso.')


def main(args):
    mirror = Mirror.create(args)
    mirror.registrar_mirror()

    print('Rodando. Precione Ctrl+C para sair')
    while True:
        solicitacao = mirror.receive()
        print(solicitacao)
        if match(protocolo.ServidorsolicitarReplicarArquivo.pattern, solicitacao):
            mirror.salvar_replica(solicitacao)


if __name__ == '__main__':
    main(sys.argv)
    exit()
