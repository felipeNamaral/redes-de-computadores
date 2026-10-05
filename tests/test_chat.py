import socket
import subprocess
import sys
import time
import pytest

HOST = '127.0.0.1'
PORTA = 5000

@pytest.fixture
def subir_servidor():
    # Sobe o processo do servidor com limite de 2 conexões antes do teste e finaliza depois.
    processo = subprocess.Popen([sys.executable, 'chatMultiusuario/servidor.py', '2'])
    time.sleep(1)  # Aguarda o servidor iniciar
    yield processo
    processo.terminate()
    processo.wait()

def conectar_cliente_teste():
    # Função auxiliar para conectar um cliente socket simples nos testes.
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORTA))
    return cliente

def test_limite_de_conexoes(subir_servidor):
    # Testa se o servidor aceita até o limite (2) e recusa o terceiro cliente.
    c1 = conectar_cliente_teste()
    c2 = conectar_cliente_teste()
    c3 = conectar_cliente_teste()

    # O terceiro cliente deve receber a mensagem de lotado e ser desconectado
    resposta = c3.recv(1024).decode('utf-8')
    assert "servidor lotado" in resposta.lower() or "lotado" in resposta.lower()

    c1.close()
    c2.close()
    c3.close()

def test_troca_de_nome(subir_servidor):
    # Testa a alteração de nome com :nome e o eco da mensagem.
    c1 = conectar_cliente_teste()
    time.sleep(0.1)
    
    # Limpa mensagens iniciais de boas-vindas/comandos
    c1.recv(1024)

    # Testa troca de nome
    c1.sendall(b":nome Tiago\n")
    time.sleep(0.1)
    resposta = c1.recv(1024).decode('utf-8')
    assert "Seu nome foi alterado para Tiago" in resposta

    c1.close()

def test_broadcast_e_eco(subir_servidor):
    # Testa se uma mensagem normal gera eco para o remetente e broadcast para os outros.
    c1 = conectar_cliente_teste()
    c2 = conectar_cliente_teste()
    time.sleep(0.2)
    
    # Limpa as mensagens iniciais de boas-vindas/comandos dos dois clientes
    c1.recv(2048)
    c2.recv(2048)

    # C1 envia uma mensagem pública
    c1.sendall(b"Ola pessoal\n")
    time.sleep(0.2)

    # 1. Verifica se C1 recebeu o Eco
    resposta_c1 = c1.recv(1024).decode('utf-8')
    assert "Voce digitou: Ola pessoal" in resposta_c1

    # 2. Verifica se C2 recebeu o Broadcast
    resposta_c2 = c2.recv(1024).decode('utf-8')
    assert "Ola pessoal" in resposta_c2

    c1.close()
    c2.close()


def test_comando_quit(subir_servidor):
    # Testa se o comando :quit desconecta o cliente corretamente.
    c1 = conectar_cliente_teste()
    time.sleep(0.2)
    
    # Limpa mensagens iniciais
    c1.recv(2048)

    # Envia o comando de saída
    c1.sendall(b":quit\n")
    time.sleep(0.2)
    
    # Verifica a mensagem de despedida enviada pelo protocolo
    resposta = c1.recv(1024).decode('utf-8')
    assert "Desconectando" in resposta
    
    # Verifica se a conexão foi realmente encerrada pelo servidor
    # (Quando o socket é fechado do outro lado, o recv retorna bytes vazios b"")
    assert c1.recv(1024) == b""
    
    c1.close()