import socket
import threading
from datetime import datetime
import time
import argparse
import queue


clientes = []


class dados:
    def __init__(self,data, nome, mensagem):
        self.data = data
        self.nome = nome
        self.mensagem = mensagem

def cria_socket():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('0.0.0.0', 5000))
    return servidor


def recebe_msg(cliente):
    conexao = cliente["conexao"]
    while True:
        try:
            mensagem = conexao.recv(1024).decode()
            if not mensagem:
                break

            data = datetime.now().strftime("%H:%M")
            dados_rec = dados(data, "", mensagem)
            cliente["memoria"].put(dados_rec)
        
        except(ConnectionError, OSError):

            break

    cliente["encerrado"].set()
    try:
        clientes.remove(cliente)
    except ValueError:
        pass

    conexao.close()


def envia_msg(cliente):
    conexao = cliente["conexao"]


    
    ultimo_horario = time.time()
    while not cliente["encerrado"].is_set():
        if (time.time() - ultimo_horario) >= 60:
            horario_atual = datetime.now().strftime("%H:%M")
            conexao.send(horario_atual.encode())
            ultimo_horario = time.time()

        try:
            dados_rec = cliente["memoria"].get(timeout=1)
        except queue.Empty:
            continue
        
        mensagem_bruta = dados_rec.mensagem
        horario_msg = dados_rec.data

        if mensagem_bruta.startswith(":"):
            if mensagem_bruta.startswith(":nome "):
                novo_nome = mensagem_bruta.split(":nome ", 1)[1]
                cliente["nome"] = novo_nome
                    
                print(f"Cliente mudou de nome para {novo_nome}.")
                conexao.sendall(f"Seu nome foi alterado para {novo_nome}".encode())

        
            elif mensagem_bruta == ":quit":
                print(f"Cliente {cliente['nome']} desconectado.")
                cliente["encerrado"].set()
                try:
                    clientes.remove(cliente)
                except ValueError:
                    pass

                try:
                    conexao.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

                conexao.close()
                break

        else:
            eco = f"Você digitou: {mensagem_bruta}"
            msg_chat = f"{horario_msg} <{cliente['nome']}>: {mensagem_bruta}"

            conexao.sendall(eco.encode())

           
                


parser = argparse.ArgumentParser(description="Servidor")
parser.add_argument(
    "maximoDeconexoes",
    type=int,
    help="Número máximo de conexoes"
)

argumentos = parser.parse_args()
maximoDeconexoes = argumentos.maximoDeconexoes


if maximoDeconexoes < 1:
    parser.error("O número máximo de conexões deve ser maior que zero")



 
servidor = cria_socket()
servidor.listen(1)
print("Servidor aguardando conexões...")

while True:
    conexao, endereco = servidor.accept()
    if(len(clientes) >= maximoDeconexoes):
            msg=f'servidor lotado!!'
            conexao.send(msg.encode())
            conexao.close()
            continue


    cliente={
        "conexao": conexao,
        "endereco": endereco,
        "nome": f"{endereco[0]}:{endereco[1]}",
        "memoria":queue.Queue(),
        "encerrado": threading.Event()
    }        

    clientes.append(cliente)

    
    print("Cliente conectado:", endereco)

    msg_conexao = f'{datetime.now().strftime("%H:%M")}: CONECTADO!!'
    conexao.send(msg_conexao.encode())

    msg_comandos = f'\n\n=========================\nComandos disponíveis:\n:nome <novo_nome> - Alterar nome do cliente\n:quit - Desconectar do servidor\n========================='
    conexao.send(msg_comandos.encode())


    thread_1 = threading.Thread(target=recebe_msg, args=(cliente,))
    thread_2 = threading.Thread(target=envia_msg, args=(cliente,))
    cliente["threads"] = [thread_1, thread_2]
    thread_1.start()
    thread_2.start()

