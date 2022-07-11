# deposito-de-arquivo-com-replicacao

## Setup
Requisitos:
- Python 3.10
- Poetry

Execução do projeto
- `poetry install`
- `python main.py`

## Funcionalidades da aplicação
A aplicação permite iniciar múltiplos clientes e servidores.
Seguindo o menu de configuração ao executar um dos três arquivos (main.py, client.py, server.py),
a aplicação será iniciada de acordo com as informações escolhidas e digitadas.

Ao entrar pelo arquivo principal da aplicação, será exibido o menu de opções, onde o usuário pode escolher se vai participar como cliente ou servidor.

Após a escolha (ou se entrar na aplicação a partir de `client.py` ou `server.py`), a aplicação irá pedir mais informações, dependendo de como o usuário vai participar.
- Se participar como Servidor, obviamente será necessário saber em qual porta o Servidor deve iniciar. Após isso, o Servidor irá iniciar e aguardar conexões de clientes.
- Se participar como Cliente, será necessário saber o host e porta do Servidor, além de um identificador do Cliente, caso ele esteja desejando se reconectar com um servidor. Após se conectar, será possível depositar ou recuperar arquivos por meio do menu de opções. Tais opções são descritas abaixo.

### Depósito de arquivo
O Cliente será capaz de solicitar depósito de arquivos, informando dados que serão descritos posteriormente.

Estrutura:  
`id_cliente:{}|qtd_replicas:{}|tamanho_arquivo:{}|hash_arquivo:{}|nome_arquivo:{}`
 - Substituindo as chaves pelos valores descritos antes do ponto-e-vírgula.

### Recuperação de arquivo
O Cliente pode solicitar a recuperação de um arquivo depositado anteriormente.
- Mesmo que o cliente se desconecte e reconecte do servidor em algum momento,
ainda será possível recuperar o arquivo graças ao seu identificador,
que será informado em toda mensagem ao servidor.

Estrutura:  
`id_cliente:{}|nome_arquivo:{}`
 - Substituindo as chaves pelos valores descritos antes do ponto-e-vírgula.

## Rascunho
onde ficarão as replicas
 - outros servidore
 - outros clientes

Quando que muda a quantidade de replicas?
    - quando o cliente pede para criar um arquivo igual
    - opção de editar replicas

Arquivos serão compartilhados entre clientes?
    - não

terão vários cliente?
    - sim


