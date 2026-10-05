import socket

def enviar_linha(conexao, texto):
    conexao.sendall((texto + '\n').encode('utf-8'))


def receber_linhas(conexao):
    buffer = b''
    while True:
        try:
            dados = conexao.recv(1024)
        except socket.timeout:
            continue # Se estourar o tempo por ociosidade, continua escutando normalmente
        except OSError: # Uma falha real de rede ocorreu (ex: cabo desconectado, programa fechado à força).
            break
        if not dados:
            break

        buffer += dados
        while b'\n' in buffer:
            linha, buffer = buffer.split(b'\n', 1)
            yield linha.decode('utf-8')
