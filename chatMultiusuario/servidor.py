import socket
import threading
from datetime import datetime
import time
import argparse
import queue
import protocolo # Importar protocolo.py criado
from transporte import receber_linhas

clientes = []
registro_lock = threading.Lock() # Lock para proteger a lista global de clientes

class dados:
    def __init__(self,data, nome, mensagem):
        self.data = data
        self.nome = nome
        self.mensagem = mensagem

def cria_socket(): # Permite que os clientes encontrem e se liguem ao sistema através da rede de porta 5000.
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
         servidor.bind(('0.0.0.0', 5000))
         servidor.listen()
    except OSError:
        servidor.close()
        raise

    return servidor

def enviar_para(sessao, texto): # Executa os envios de forma sequencial e segura com lock_envio.
    with sessao["lock_envio"]:
        try:
            sessao["conexao"].sendall((texto + '\n').encode())
        except (ConnectionError, OSError): # Tratamento de erros de conexão e encerramento do socket.
            encerrar_cliente(sessao)

def listar_sessoes():
    # Faz um registro_lock para a lista global de clientes para garantir uma leitura segura das variáveis compartilhadas.
    with registro_lock:
        return list(clientes)

def encerrar_cliente(sessao):
    # Verifica se a flag 'encerrado' ainda é falsa para evitar idempotência.
    if not sessao["encerrado"].is_set():
        sessao["encerrado"].set()
        
        with registro_lock: # Garantia que nenhuma outra thread esteja acessando a lista de clientes ao mesmo tempo.
            if sessao in clientes: # Checa se o cliente ainda está na lista antes de tentar removê-lo, evitando erros de remoção duplicada.
                clientes.remove(sessao) # Remove o cliente da lista global de clientes, garantindo que ele não receba mais mensagens e liberando o servidor.
                
        try: # Inicia a tentativa de encerrar a conexão do cliente de forma segura, tratando possíveis exceções.
            sessao["conexao"].shutdown(socket.SHUT_RDWR) # Força o encerramento da conexão, interrompendo qualquer operação de envio ou recebimento.
        except OSError: # Se a conexão de rede já estiver rompida (erro de tubulação quebrada), o Python levanta um OSError.
            pass # Ignora a falha silenciosamente, pois o objetivo já era encerrar a conexão.
        sessao["conexao"].close() # Fecha o socket do cliente, liberando recursos do sistema e garantindo que a conexão seja encerrada de forma limpa.


def recebe_msg(cliente):
    conexao = cliente["conexao"]
    try:
        for mensagem in receber_linhas(conexao):
            data = datetime.now().strftime("%H:%M")
            dados_rec = dados(data, "", mensagem)
            cliente["memoria"].put(dados_rec)
    except (OSError, UnicodeDecodeError) as erro:
        print(f"Erro ao receber mensagem de {cliente['nome']}: {erro}")
    finally:
        encerrar_cliente(cliente)


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



try:
    servidor = cria_socket()
except OSError as erro:
    print(f"Não foi possível iniciar o servidor: {erro}")
    raise SystemExit(1)


print("Servidor aguardando conexões...")

while True:

    try:
        conexao, endereco = servidor.accept()
    except OSError as erro:
        print(f"Erro ao aceitar conexão: {erro}")
        continue 


    with registro_lock:
        lotado = len(clientes) >= maximoDeconexoes    
    if(lotado):
        msg=f'servidor lotado!!\n'
        try:
            conexao.sendall(msg.encode())
        except OSError as erro:
            print(f"Erro ao enviar mensagem de servidor lotado para o cliente {endereco}: {erro}")
        finally:
            conexao.close()
        continue
                

    with registro_lock:  # Evita race conditions.

        cliente={
            "conexao": conexao,
            "endereco": endereco,
            "nome": f"{endereco[0]}:{endereco[1]}",
            "memoria": queue.Queue(),
            "encerrado": threading.Event(),
            "lock_envio": threading.Lock()
        }
        
        clientes.append(cliente)     

    
    print("Cliente conectado:", endereco)

    try:
        with cliente["lock_envio"]:
            msg_conexao = f'{datetime.now().strftime("%H:%M")}: CONECTADO!!\n'
            conexao.sendall(msg_conexao.encode())

            msg_comandos = f'\n=========================\nComandos disponíveis:\n:nome <novo_nome> - Alterar nome do cliente\n:quit - Desconectar do servidor\n=========================\n'
            conexao.sendall(msg_comandos.encode())
    except OSError as erro:
        print(f"Erro ao enviar mensagens iniciais para o cliente {endereco}: {erro}")
        encerrar_cliente(cliente)
        continue




    thread_1 = threading.Thread( #Fica dedicada exclusivamente a escutar o socket do cliente com a função recebe_msg, que lê as mensagens enviadas pelo cliente e as coloca na fila de memória.
            target=recebe_msg, 
            args=(cliente,)
            )     
    thread_2 = threading.Thread( # Fica responsável por tirar as mensagens da fila e decidir o que fazer com elas (enviar aos outros, processar comandos ou enviar avisos de horário).
            target=protocolo.processar_cliente, 
            args=(cliente, enviar_para, listar_sessoes, encerrar_cliente)
        )
    
    cliente["threads"] = [thread_1, thread_2]
    thread_1.start()
    thread_2.start()

