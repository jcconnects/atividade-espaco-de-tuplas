# Atividade Prática: Espaço de Tuplas

## Pré-requisitos

- [Git](https://git-scm.com/)
- [Docker](https://docs.docker.com/get-docker/) com [Docker Compose](https://docs.docker.com/compose/)

Verifique com:
```bash
docker compose version
```

---

## Contexto histórico

Em 1985, David Gelernter propôs a linguagem de coordenação **Linda**, que introduziu o conceito de **espaço de tuplas** (*tuple space*): uma memória associativa compartilhada onde processos depositam e retiram tuplas sem se conhecerem diretamente. Um processo que escreve uma tupla não sabe quem vai lê-la; um processo que lê uma tupla não sabe quem a escreveu. A única coisa compartilhada é o **espaço** — daí o nome *desacoplamento espacial*.

Esse modelo simples e poderoso está na origem de sistemas que você provavelmente já ouviu falar: **RabbitMQ**, **Apache Kafka**, **Redis Streams** e **Google Pub/Sub**. Nesta atividade, você vai construir esse mecanismo do zero, entender como ele funciona por dentro, e no final traçar o caminho da Linda até esses sistemas modernos.

---

## Objetivos

Ao final desta atividade, você será capaz de:

1. Explicar as operações `OUT`, `IN` e `RD` de um espaço de tuplas e a diferença entre leitura destrutiva e não-destrutiva.
2. Identificar o **desacoplamento espacial**: por que produtor e consumidor não precisam se conhecer e como isso é viabilizado pelo espaço compartilhado.
3. Conectar o modelo de espaço de tuplas às abstrações modernas de mensageria (filas, streams, eventos).

---

## Fase pré-atividade

Antes da aula, estude os seguintes materiais:

1. **Leitura (15 min):** [Linda in Context — David Gelernter (1989)](https://dl.acm.org/doi/10.1145/63334.63337) — leia o resumo e a seção 2 ("The Tuple Space").
2. **Vídeo (12 min):** [What is a Message Queue?](https://www.youtube.com/watch?v=xErwDaOc-Gs) — contexto de onde sistemas de mensageria são usados.

---

## Estrutura do projeto

```
atividade-espaco-de-tuplas/
├── docker-compose.yml         ← orquestra os 5 serviços
├── espaco/
│   ├── espaco.py              ← o espaço de tuplas (servidor central)
│   └── Dockerfile
├── produtor/
│   ├── produtor.py            ← deposita tarefas com OUT
│   └── Dockerfile
├── consumidor-a/
│   ├── consumidor.py          ← retira tarefas com IN (bloqueante)
│   └── Dockerfile
├── consumidor-b/
│   ├── consumidor.py          ← código idêntico ao consumidor-a
│   └── Dockerfile
└── leitor/
    ├── leitor.py              ← lê resultados com RD (sem remover)
    └── Dockerfile
```

Observe o `docker-compose.yml`: nenhum dos quatro clientes tem uma referência direta a qualquer outro cliente. Todos se conectam apenas ao serviço `espaco`. Essa topologia reflete diretamente o conceito de desacoplamento espacial.

---

## Nível 0 — Rodar

Execute:

```bash
docker compose up --build
```

Aguarde todos os serviços iniciarem. Você verá logs intercalados de todos os cinco serviços. O servidor `espaco` imprime o estado do espaço após cada operação:

```
espaco-1       | ╔══════════════════════════════════════════╗
espaco-1       | ║  [OUT ['tarefa', 'processar', 1]]        ║
espaco-1       | ╠══════════════════════════════════════════╣
espaco-1       | ║  ['tarefa', 'processar', 1]              ║
espaco-1       | ╚══════════════════════════════════════════╝
produtor-1     | [PRODUTOR] OUT: ['tarefa', 'processar', 1]
consumidor-a-1 | [CONSUMIDOR-A] IN obteve: ['tarefa', 'processar', 1]
espaco-1       | ╔══════════════════════════════════════════╗
espaco-1       | ║  [IN  ['tarefa', 'processar', 1]]        ║
espaco-1       | ╠══════════════════════════════════════════╣
espaco-1       | ║  (espaço vazio)                          ║
espaco-1       | ╚══════════════════════════════════════════╝
```

**Observe e responda (anote no relatório):**

1. O produtor menciona o nome de algum consumidor em algum momento? O consumidor menciona o nome do produtor?
2. Quando duas tarefas estão no espaço ao mesmo tempo, o que os dois consumidores fazem? Cada tarefa é processada por um ou por dois consumidores?
3. O `leitor` também consome as tarefas junto com os consumidores? Por que não?

Encerre com `Ctrl+C`.

---

## Nível 1 — Inspecionar

Abra e leia os arquivos `espaco/espaco.py`, `produtor/produtor.py` e `consumidor-a/consumidor.py`.

### 1.1 As três operações

O espaço de tuplas expõe três operações. Preencha a tabela no relatório para cada uma:

| Operação | O que ela faz? | Bloqueia quando não encontra correspondência? | Altera o estado do espaço? |
|----------|----------------|----------------------------------------------|---------------------------|
| `OUT` | | | |
| `IN`  | | | |
| `RD`  | | | |

### 1.2 Mecanismo de bloqueio

Localize no código de `espaco.py` a estrutura que faz `IN` e `RD` aguardarem quando não há tupla correspondente. Responda:

- Qual classe do módulo `threading` é usada?
- O que o método `.wait()` faz nesse contexto?
- O que o método `.notify_all()` faz, e quem o chama?

### 1.3 Casamento de padrões (*pattern matching*)

O consumidor chama `IN` com o padrão `["tarefa", "processar", None]`. Localize a função `_casa` em `espaco.py` e explique:

- O que `None` significa dentro de um padrão?
- Esse padrão casaria com a tupla `["tarefa", "processar", 7]`? E com `["tarefa", "entregar", 3]`? Por quê?

### 1.4 Desacoplamento espacial

- O produtor tem alguma variável que aponta para um consumidor? Os consumidores têm alguma variável que aponta para o produtor?
- Como eles se coordenam, então?

### 1.5 Experimentos dirigidos

**Experimento 1 — Remover um consumidor:**

No arquivo `docker-compose.yml`, comente o bloco inteiro do serviço `consumidor-b` (adicione `#` antes de cada linha do bloco). Salve e execute novamente:

```bash
docker compose up --build
```

As cinco tarefas ainda são processadas? Alguma tarefa se perde? O que isso diz sobre o papel do espaço de tuplas?

**Experimento 2 — Produtor rápido, consumidor lento:**

No `produtor/produtor.py`, mude `time.sleep(1)` para `time.sleep(0)`. No `consumidor-a/consumidor.py`, mude `time.sleep(0.5)` para `time.sleep(2)`. Execute:

```bash
docker compose up --build
```

Observe o estado do espaço enquanto o produtor publica todas as tarefas. Descreva o que acontece.

Restaure os valores originais antes de continuar.

---

## Nível 2 — Modificar

### Modificação A — Prioridade de tarefas (guiada)

Neste exercício, você vai adicionar um campo de **prioridade** às tarefas sem alterar a lógica dos consumidores existentes — apenas acrescentando um campo a mais nas tuplas.

**No `produtor/produtor.py`**, substitua a lista `TAREFAS` por:

```python
TAREFAS = [
    ["tarefa", "processar", 1, 2],  # prioridade baixa
    ["tarefa", "processar", 2, 1],  # prioridade alta
    ["tarefa", "processar", 3, 2],  # prioridade baixa
    ["tarefa", "processar", 4, 1],  # prioridade alta
    ["tarefa", "processar", 5, 1],  # prioridade alta
]
```

**No `consumidor-a/consumidor.py` e `consumidor-b/consumidor.py`**, modifique a função `main` para que o consumidor tente buscar primeiro uma tarefa de alta prioridade (`prioridade = 1`). Se não encontrar em até 1 segundo, busca qualquer tarefa:

```python
# dica: você precisará de duas chamadas IN com padrões diferentes
# e de uma forma de tentar uma antes da outra
# o espaço de tuplas não tem timeout nativo — como você resolve isso?
```

Execute e verifique nos logs se as tarefas de alta prioridade (ids 2, 4, 5) foram processadas antes das de baixa prioridade (ids 1, 3).

### Modificação B — Serviço monitor (aberta)

Sem modificar o produtor nem os consumidores, adicione um novo serviço `monitor` que, a cada 2 segundos, exibe quantas tarefas estão pendentes no espaço e quantos resultados já foram produzidos.

Você precisará criar:

- `monitor/monitor.py`
- `monitor/Dockerfile`
- Adicionar o serviço `monitor` no `docker-compose.yml`

**Dica de design:** Por que você deve usar `RD` e não `IN` no monitor? O que aconteceria se o monitor usasse `IN`?

**Desafio:** O protocolo Linda não tem uma operação `COUNT`. Como você contaria o número de tuplas que casam com um padrão usando apenas `RD`? (Discuta essa limitação no relatório — ela é real e é um dos motivos pelos quais sistemas modernos como Redis expõem operações como `LLEN`.)

---

## Da Linda aos sistemas modernos

O modelo que você implementou nesta atividade — processos que se coordenam através de um espaço compartilhado sem se conhecerem diretamente — é o fundamento de toda a mensageria moderna:

| Conceito no espaço de tuplas | Equivalente moderno |
|------------------------------|---------------------|
| `OUT(tupla)` | Publish / Produce (RabbitMQ, Kafka) |
| `IN(padrão)` | Consume with ack — mensagem é removida da fila |
| `RD(padrão)` | Peek / Subscribe — mensagem permanece no tópico |
| Espaço compartilhado | Broker (RabbitMQ exchange, Kafka topic) |
| Padrão de casamento | Routing key, topic filter, consumer group |
| Bloqueio em `IN` | Long-polling, push-based delivery |

A principal diferença entre o espaço de tuplas da Linda e um broker moderno é **escala e persistência**: brokers como Kafka armazenam mensagens em disco, replicam entre servidores, e atendem milhões de mensagens por segundo. O modelo conceitual, porém, é o mesmo que você acabou de implementar com ~120 linhas de Python.

---

## Entregável

1. Faça um *fork* (ou clone) deste repositório.
2. Complete os Níveis 1 e 2, incluindo as modificações nos arquivos de código.
3. Preencha o `relatorio-template.md` com suas respostas.
4. Envie o link do repositório com seus commits (ou o arquivo `.zip` do projeto com o relatório preenchido), conforme orientação do professor.

---

## Dúvidas

Abra uma *issue* neste repositório ou traga sua pergunta para a próxima aula.
