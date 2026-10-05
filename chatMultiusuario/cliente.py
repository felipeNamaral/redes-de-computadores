import socket
import threading

from transporte import enviar_linha, receber_linhas

IP_SERVIDOR = '127.0.0.1'
PORTA_SERVIDOR = 5000


def cria_socket():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((IP_SERVIDOR, PORTA_SERVIDOR))
    except (OSError, KeyboardInterrupt):
        cliente.close()
        raise
    return cliente


def envia_msg(conexao):
    while True:
        try:
            mensagem = input()
            print('\033[F\033[K', end='')
            enviar_linha(conexao, mensagem)

            if mensagem.strip() == ":quit": # Interrompe a leitura do teclado
                break

        except (EOFError, ConnectionError, OSError):
            # Libera a thread de recebimento se o teclado ou o envio falhar.
            try:
                conexao.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            break

 
def recebe_msg(conexao):
    try:
        for mensagem in receber_linhas(conexao):
            print(mensagem)
    except (OSError, UnicodeDecodeError) as erro:
        print(f'Conexao encerrada: {erro}')


cliente = None

try:
    cliente = cria_socket()

    thread_1 = threading.Thread(target=envia_msg, args=(cliente,), daemon=True)
    thread_2 = threading.Thread(target=recebe_msg, args=(cliente,), daemon=True)

    thread_1.start()
    thread_2.start()

    thread_2.join()
except OSError as erro:
    print(f'Nao foi possivel conectar ao servidor: {erro}')
except KeyboardInterrupt:
    print('\nCliente encerrado.')
finally:
    if cliente is not None:
        # shutdown interrompe recv mesmo se outra thread estiver esperando dados.
        try:
            cliente.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        cliente.close()
