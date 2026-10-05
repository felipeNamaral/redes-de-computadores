import time
import queue
from datetime import datetime

# Cores ANSI
COR_SISTEMA = "\033[93m" # Amarelo
COR_AVISO = "\033[96m" # Ciano
COR_ERRO = "\033[91m" # Vermelho
COR_MENSAGEM = "\033[92m" # Verde
RESET = "\033[0m" # Restaura a cor padrão

def processar_cliente(sessao, enviar_para, listar_sessoes, encerrar_cliente):
    ultimo_horario = time.monotonic()

    while not sessao["encerrado"].is_set():
        if time.monotonic() - ultimo_horario >= 60:
            horario_atual = datetime.now().strftime("%H:%M")
            enviar_para(sessao, f"{COR_SISTEMA}{horario_atual}{RESET}")
            ultimo_horario = time.monotonic()

        try:
            dados_rec = sessao["memoria"].get(timeout=1)
        except queue.Empty:
            continue

        mensagem_bruta = dados_rec.mensagem.strip()
        horario_msg = dados_rec.data

        if mensagem_bruta.startswith(":"):
            partes = mensagem_bruta.split(" ", 1)
            comando = partes[0]

            if comando == ":nome":
                if len(partes) > 1 and partes[1].strip():
                    novo_nome = partes[1].strip()
                    nome_antigo = sessao["nome"]          
                    sessao["nome"] = novo_nome
                    print(f"[{horario_msg}] '{nome_antigo}' alterou o nome para '{novo_nome}'")
                    enviar_para(sessao, f"{COR_SISTEMA}Seu nome foi alterado para {novo_nome}{RESET}")
                else:
                    enviar_para(sessao, f"{COR_ERRO}Comando invalido: Nome nao pode ser vazio.{RESET}")
            elif comando == ":quit" and len(partes) == 1:
                enviar_para(sessao, f"{COR_SISTEMA}Desconectando do servidor...{RESET}")
                encerrar_cliente(sessao)
                break
            else:
                enviar_para(sessao, f"{COR_ERRO}Comando desconhecido: {comando}{RESET}")
        
        else:
            eco = f"{COR_AVISO}Voce digitou:{RESET} {mensagem_bruta}"
            enviar_para(sessao, eco)

            msg_publica = f"{COR_MENSAGEM}{sessao['nome']}{RESET} ({horario_msg}): {mensagem_bruta}"

            sessoes_ativas = listar_sessoes()
            for outra_sessao in sessoes_ativas:
                if outra_sessao != sessao:
                    enviar_para(outra_sessao, msg_publica)