import time
import queue
from datetime import datetime

def processar_cliente(sessao, enviar_para, listar_sessoes, encerrar_cliente):
    ultimo_horario = time.monotonic()

    while not sessao["encerrado"].is_set():
        if time.monotonic() - ultimo_horario >= 60:
            horario_atual = datetime.now().strftime("%H:%M")
            enviar_para(sessao, horario_atual)
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
                    sessao["nome"] = novo_nome
                    enviar_para(sessao, f"Seu nome foi alterado para {novo_nome}")
                else:
                    enviar_para(sessao, "Comando invalido: Nome nao pode ser vazio.")
            elif comando == ":quit" and len(partes) == 1:
                enviar_para(sessao, "Desconectando do servidor...")
                encerrar_cliente(sessao)
                break
            else:
                enviar_para(sessao, f"Comando desconhecido: {comando}")
        
        else:
            eco = f"Voce digitou: {mensagem_bruta}"
            enviar_para(sessao, eco)

            msg_publica = f"{sessao['nome']} ({horario_msg}): {mensagem_bruta}"

            sessoes_ativas = listar_sessoes()
            for outra_sessao in sessoes_ativas:
                if outra_sessao != sessao:
                    enviar_para(outra_sessao, msg_publica)