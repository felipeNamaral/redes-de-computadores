import socket
import threading
from datetime import datetime
import time

memoria  = []
nome_cliente = ""

class dados:
    def __init__(self,data, nome, mensagem):
        self.data = data
        self.nome = nome
        self.mensagem = mensagem

def cria_socket():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('0.0.0.0', 5000))
    return servidor


def recebe_msg(conexao):
    while True:
        try:
            mensagem = conexao.recv(1024).decode()
            if not mensagem:
                break

            data = datetime.now().strftime("%H:%M")
            dados_rec = dados(data, "", mensagem)
            memoria.append(dados_rec)
        
        except(ConnectionError, OSError):
            break

        if not mensagem:
            break


def envia_msg(conexao):
    global nome_cliente
    tamanho_memoria = len(memoria)
    ultimo_horario = time.time()
    while True:
        if (time.time() - ultimo_horario) >= 60:
            horario_atual = datetime.now().strftime("%H:%M")
            conexao.send(horario_atual.encode())
            ultimo_horario = time.time()

        if len(memoria) > tamanho_memoria:
            mensagem_bruta = memoria[-1].mensagem
            horario_msg = memoria[-1].data

            if mensagem_bruta.startswith(":"):
                if mensagem_bruta.startswith(":nome "):
                    novo_nome = mensagem_bruta.split(":nome ", 1)[1]
                    nome_cliente = novo_nome
                    
                    print(f"Cliente mudou de nome para {novo_nome}.")
                    conexao.send(f"Seu nome foi alterado para {novo_nome}".encode())

        
                elif mensagem_bruta.startswith(":quit"):
                    print(f"Cliente {nome_cliente} desconectado.")
                    conexao.close()
                    break

            else:
                eco = f"Você digitou: {mensagem_bruta}"
                msg_chat = f"{horario_msg} <{nome_cliente}>: {mensagem_bruta}"

                conexao.send(eco.encode())

            tamanho_memoria = len(memoria)
                

 
servidor = cria_socket()
servidor.listen(1)
print("Servidor aguardando conexão...")
conexao, endereco = servidor.accept()

nome_cliente = f"{endereco[0]}:{endereco[1]}"
print("Cliente conectado:", endereco)

msg_conexao = f'{datetime.now().strftime("%H:%M")}: CONECTADO!!'
conexao.send(msg_conexao.encode())

msg_comandos = f'\n\n=========================\nComandos disponíveis:\n:nome <novo_nome> - Alterar nome do cliente\n:quit - Desconectar do servidor\n========================='
conexao.send(msg_comandos.encode())

thread_1 = threading.Thread(target=recebe_msg, args=(conexao,))
thread_2 = threading.Thread(target=envia_msg, args=(conexao,))
thread_1.start()
thread_2.start()

