import server
import client


if __name__ == '__main__':
    print('\n1 - Servidor\n2 - Cliente')
    opcao = int(input('Digite a opção desejada: '))
    if opcao == 1:
        server.main()
    elif opcao == 2:
        client.main()
    else:
        print('Opção inválida')
        exit()
    print('\nFim do programa')
    exit()

