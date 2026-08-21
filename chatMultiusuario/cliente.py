import socket
import threading


IP_SERVIDOR = '127.0.0.1'
PORTA_SERVIDOR = 5000


def cria_socket():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((IP_SERVIDOR, PORTA_SERVIDOR))
    return cliente


def envia_msg(conexao):
    while True:
        try:
            mensagem = input()
            conexao.send(mensagem.encode())
        except (EOFError, ConnectionError, OSError):
            break


def recebe_msg(conexao):
    while True:
        try:
            mensagem = conexao.recv(1024).decode()
        except (ConnectionError, OSError):
            break

        if not mensagem:
            break

        print(mensagem)


cliente = None

try:
    cliente = cria_socket()

    thread_1 = threading.Thread(target=envia_msg, args=(cliente,), daemon=True)
    thread_2 = threading.Thread(target=recebe_msg, args=(cliente,))

    thread_1.start()
    thread_2.start()

    thread_2.join()
except OSError as erro:
    print(f'Nao foi possivel conectar ao servidor: {erro}')
except KeyboardInterrupt:
    print('\nCliente encerrado.')
finally:
    if cliente is not None:
        cliente.close()
