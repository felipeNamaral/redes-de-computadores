import socket
import threading
from datetime import datetime
import time

memoria  = []

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
       mensagem = conexao.recv(1024).decode()
       if not mensagem:
           break


       nome, msg = mensagem.split("|", 1)
       data = datetime.now().strftime("%H:%M:%S")
       dados_rec = dados(data, nome, msg)

       if dados_rec.nome == 'null':
            dados_rec.nome = endereco[0]

       memoria.append(dados_rec)

       



def envia_msg(conexao):
    tamanho_memoria = len(memoria)
    ultimo_horario = time.time()
    while True:
        if len(memoria) > tamanho_memoria:

            mensagem = memoria[-1]
            msg = mensagem.data + " <" + mensagem.nome + ">: " + mensagem.mensagem +'veio do servidor'
            conexao.send(msg.encode())
            tamanho_memoria = len(memoria)

        if (time.time() - ultimo_horario) >= 60:
           conexao.send((datetime.now().strftime("%H:%M:%S")).encode())
           ultimo_horario = time.time()
           
                


servidor = cria_socket()
servidor.listen(1)
print("Servidor aguardando conexão...")
conexao, endereco = servidor.accept()
conexao.send(('Servidor <' + datetime.now().strftime("%H:%M:%S") + '>: CONECTADO!!').encode())
print("Cliente conectado:", endereco)

thread_1 = threading.Thread(target=recebe_msg, args=(conexao,))
thread_2 = threading.Thread(target=envia_msg, args=(conexao,))
thread_1.start()
thread_2.start()

