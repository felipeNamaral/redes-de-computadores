def enviar_linha(conexao, texto):
    conexao.sendall((texto + '\n').encode('utf-8'))


def receber_linhas(conexao):
    buffer = b''
    while True:
        dados = conexao.recv(1024)
        if not dados:
            break

        buffer += dados
        while b'\n' in buffer:
            linha, buffer = buffer.split(b'\n', 1)
            yield linha.decode('utf-8')
