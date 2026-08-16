# Projeto Pratico 1 - Redes de Computadores

## Tema

Chat multiusuario em arquitetura cliente/servidor utilizando sockets e threads.

Nesta primeira parte do projeto, o chat deve funcionar com apenas um usuario remoto conectado ao servidor. A estrutura, no entanto, ja deve seguir o modelo necessario para comunicacao bidirecional assincrona, com threads separadas para envio, recebimento e processamento das mensagens.

## Integrantes

| Nome | RA |
| --- | --- |
| Felipe Amaral | 24792566 |
| Pedro Pimentel | 24023362 |
| Tiago Lanca | 25004196 |

## Objetivo

Desenvolver uma aplicacao de rede no modelo cliente/servidor para uma sala de bate-papo. O sistema deve permitir que um cliente se conecte ao servidor, envie mensagens, altere seu nome de usuario e encerre a conexao por meio de comandos definidos.

O projeto pratica os seguintes conceitos da disciplina de Redes de Computadores:

- uso de sockets;
- comunicacao cliente/servidor;
- comunicacao bidirecional assincrona;
- uso de threads;
- compartilhamento de dados entre threads;
- interpretacao de comandos enviados pela rede.

## Funcionamento Geral

Ao iniciar a conexao, o cliente deve receber imediatamente uma mensagem do servidor no formato:

```text
<HORARIO>: CONECTADO!!
```

Apos a conexao, tanto o cliente quanto o servidor devem trabalhar com duas threads principais associadas ao socket:

- Thread 1: responsavel por receber entradas/comandos e enviar dados pela conexao.
- Thread 2: responsavel por receber dados da conexao, processar eventos periodicos e imprimir as informacoes na tela.

No servidor, as mensagens e comandos recebidos devem ser armazenados em uma estrutura de dados compartilhada. Uma thread do servidor deve verificar periodicamente essa area compartilhada e executar a acao correspondente.

## Requisitos do Chat

O servidor deve enviar ao cliente, a cada minuto, a data e o horario atual, mesmo que o chat esteja ocioso.

O cliente deve permitir que o usuario digite:

- uma mensagem comum, que sera enviada ao chat;
- o comando `:nome <NOME>`, usado para alterar o nome do usuario;
- o comando `:quit`, usado para sair da aplicacao.

Textos iniciados com `:` devem ser interpretados como comandos. Textos que nao iniciam com `:` devem ser tratados como mensagens comuns.

Caso o usuario nao defina um nome, o sistema deve utilizar automaticamente a identificacao:

```text
<IP_DO_CLIENTE>:<PORTA_DO_CLIENTE>
```

## Formato das Mensagens

Mensagens recebidas pelos usuarios devem seguir o formato:

```text
NOME_DO_USUARIO (horario): MENSAGEM
```

Para o usuario que enviou a mensagem, o servidor deve retornar um eco no formato:

```text
Voce digitou: MENSAGEM
```

## Comandos

| Comando | Descricao |
| --- | --- |
| `:nome <NOME>` | Define ou altera o nome do usuario no chat. |
| `:quit` | Encerra a participacao do usuario e fecha a aplicacao. |
| `MENSAGEM` | Envia uma mensagem comum para o chat. |

## Arquitetura Esperada

```text
Cliente
├── Thread de envio
│   └── le comandos/mensagens do teclado e envia ao servidor
└── Thread de recebimento
    └── recebe mensagens do servidor e imprime na tela

Servidor
├── Thread de recebimento
│   └── recebe dados do cliente e armazena em memoria compartilhada
└── Thread de processamento/envio
    └── processa comandos, envia mensagens e publica data/hora periodicamente
```

## Fluxo Basico

1. O servidor e iniciado e fica aguardando conexoes.
2. O cliente inicia uma conexao com o servidor.
3. O servidor envia a mensagem `<HORARIO>: CONECTADO!!`.
4. O cliente pode enviar mensagens ou comandos.
5. O servidor interpreta os dados recebidos.
6. O servidor retorna o eco da mensagem ou executa o comando solicitado.
7. A cada minuto, o servidor envia a data e o horario atual ao cliente.
8. O usuario pode encerrar a aplicacao com `:quit`.


