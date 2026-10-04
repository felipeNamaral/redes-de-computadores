# Projeto Prático 1 — Redes de Computadores

Chat multiusuário desenvolvido em Python, utilizando sockets TCP e threads para comunicação bidirecional assíncrona entre clientes e servidor.

Documentação preparada para a versão final das três fases. A descrição da entrega inclui o comportamento previsto para a integração da Fase 3; a validação do código deve ser realizada separadamente.

## Integrantes

| Nome | RA |
| --- | --- |
| Felipe Amaral | 24792566 |
| Pedro Pimentel | 24023362 |
| Tiago Lança | 25004196 |

## Objetivo

Implementar uma sala de bate-papo na qual vários usuários podem trocar mensagens públicas, alterar seu nome e solicitar a desconexão. O projeto aplica conceitos de sockets, threads, memória compartilhada, sincronização e tratamento de exceções.

## Fase 1 — Comunicação cliente/servidor

A primeira fase estabelece a comunicação TCP com um cliente remoto. Após a conexão, o servidor envia uma confirmação no formato:

```text
14:30: CONECTADO!!
```

O cliente possui uma thread para ler o teclado e enviar mensagens, e outra para receber e exibir as respostas. No servidor, uma thread recebe os dados e os armazena em memória compartilhada, enquanto outra processa as mensagens e os comandos.

### Comandos

| Entrada | Ação |
| --- | --- |
| `:nome Ana` | Define ou altera o nome do usuário. |
| `:quit` | Solicita ao servidor a desconexão e encerra a participação do cliente. |
| `Olá, pessoal!` | Envia uma mensagem pública para a sala. |

Textos iniciados com `:` são interpretados como comandos. Os demais são mensagens comuns. Nomes vazios e comandos desconhecidos recebem uma resposta de erro. Quando nenhum nome é definido, o servidor utiliza `IP:PORTA` do cliente.

O remetente recebe um eco:

```text
Voce digitou: Olá, pessoal!
```

Os demais participantes recebem a identificação do remetente, o horário e a mensagem:

```text
Ana (14:30): Olá, pessoal!
```

O comportamento previsto para a entrega inclui o envio de data e horário a cada minuto, mesmo quando não há mensagens na sala.

## Fase 2 — Atendimento de múltiplos clientes

O servidor mantém um laço de aceitação de conexões e cria uma sessão independente para cada cliente. Cada sessão contém:

- Socket e endereço do cliente.
- Nome de usuário.
- Fila de mensagens recebidas.
- Evento de encerramento.
- Lock de envio e referências às threads.

Cada cliente possui duas threads no servidor: recebimento e processamento/envio. A alteração de nome e os comandos afetam somente a sessão solicitante. As mensagens públicas são distribuídas aos demais participantes; o remetente recebe o eco.

O limite de clientes simultâneos é informado por argumento de linha de comando. Quando esse limite é atingido, o servidor envia `servidor lotado!!` e fecha a conexão excedente, sem enviar a confirmação de entrada.

Ao desconectar um cliente, o servidor remove sua sessão e libera a vaga. Uma nova conexão pode ocupar essa vaga sem reiniciar o servidor. A quantidade de sessões ativas é obtida por `len(clientes)`; o parâmetro de `listen()` não representa esse limite.

## Fase 3 — Controle de exceções

A terceira fase reúne o tratamento de falhas de conexão e a manutenção das sessões para preservar o atendimento dos demais usuários.

### Cliente

O cliente trata falhas ao conectar e erros de socket durante a comunicação. Quando o servidor fecha a conexão, o recebimento termina e o fluxo principal libera o socket. Para realizar outra tentativa após uma falha de conexão, o usuário executa o cliente novamente.

### Servidor

O servidor trata erros na inicialização do socket, associação à porta, escuta, aceitação de conexões e envio de mensagens.

- Se a inicialização falhar, informa o problema e encerra; o socket criado é fechado quando a falha ocorre em `bind()` ou `listen()`.
- Se a aceitação falhar, informa o erro e volta a aguardar conexões.
- Se o envio do aviso de lotação falhar, fecha a conexão excedente mesmo assim.
- Se o envio das boas-vindas falhar, encerra a sessão e libera a vaga.
- Quando recebe EOF ou uma falha de socket tratada, remove a sessão e fecha sua conexão.

O registro compartilhado é protegido por `registro_lock`. Cada sessão possui seu próprio `lock_envio`, para serializar mensagens destinadas àquela conexão. A fila de entrada é uma `queue.Queue`, apropriada para comunicação entre threads.

### Critérios da entrega integrada

A versão final deve preservar mensagens completas mesmo quando o TCP fragmenta ou agrupa os dados, liberar recursos nas falhas, manter a independência das sessões e continuar aceitando clientes após desconexões. O critério de qualidade da Fase 3 é não apresentar exceções não tratadas ou warnings do interpretador/runtime durante o uso.

## Estrutura do projeto

| Arquivo | Responsabilidade |
| --- | --- |
| `chatMultiusuario/servidor.py` | Conexões, sessões, filas, limite de clientes e limpeza dos sockets. |
| `chatMultiusuario/cliente.py` | Entrada pelo teclado, envio e exibição das respostas. |
| `chatMultiusuario/protocolo.py` | Comandos, nomes, eco, broadcast e avisos periódicos. |
| `chatMultiusuario/transporte.py` | Envio de linhas UTF-8 e reconstrução de mensagens delimitadas por quebra de linha. |

## Requisitos de execução

- Python 3 instalado.
- Um terminal para o servidor e um para cada cliente.
- Porta TCP 5000 disponível no servidor.

A execução do chat utiliza somente a biblioteca padrão do Python, sem instalação de pacotes adicionais.

## Como executar

Abra os terminais na pasta raiz do projeto.

### Iniciar o servidor

```console
python chatMultiusuario/servidor.py 3
```

O argumento `3` é o máximo de clientes simultâneos. Ele é obrigatório e deve ser um inteiro positivo.

O servidor escuta em `0.0.0.0:5000`, permitindo conexões pelas interfaces IPv4 do computador.

### Iniciar os clientes

Execute em cada terminal adicional:

```console
python chatMultiusuario/cliente.py
```

O endereço padrão é `127.0.0.1:5000`, para cliente e servidor no mesmo computador. Para utilizar computadores diferentes, altere `IP_SERVIDOR` em `chatMultiusuario/cliente.py` para o IPv4 do computador servidor. A rede e o firewall precisam permitir a conexão à porta TCP 5000.

Dependendo da instalação, substitua `python` por `py` no Windows ou `python3` em outros ambientes.

### Exemplo de utilização

No primeiro cliente:

```text
:nome Ana
Olá, pessoal!
```

No segundo cliente:

```text
:nome Beto
Olá, Ana!
```

Para sair de um cliente:

```text
:quit
```

A saída de um participante libera sua vaga e mantém os demais na sala. O servidor permanece em execução para receber novas conexões.
