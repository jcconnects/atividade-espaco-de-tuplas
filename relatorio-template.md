# Relatório — Atividade Prática: Espaço de Tuplas

**Disciplina:**
**Dupla:** /
**Data:**

---

## Nível 1 — Inspecionar o código

### 1.1 As três operações do espaço de tuplas

Preencha a tabela com base na leitura de `espaco/espaco.py`:

| Operação | O que ela faz? | Bloqueia quando não encontra correspondência? | Altera o estado do espaço? |
|----------|----------------|----------------------------------------------|---------------------------|
| `OUT(tupla)` | | | |
| `IN(padrão)` | | | |
| `RD(padrão)` | | | |

### 1.2 Mecanismo de bloqueio

Qual classe do módulo `threading` é responsável pelo bloqueio em `IN` e `RD`?

> _Resposta:_

O que o método `.wait()` faz nesse contexto?

> _Resposta:_

O que o método `.notify_all()` faz, e quem o chama?

> _Resposta:_

### 1.3 Casamento de padrões

O que significa `None` em uma posição do padrão?

> _Resposta:_

O padrão `["tarefa", "processar", None]` casa com a tupla `["tarefa", "processar", 7]`? Por quê?

> _Resposta:_

O padrão `["tarefa", "processar", None]` casa com a tupla `["tarefa", "entregar", 3]`? Por quê?

> _Resposta:_

### 1.4 Desacoplamento espacial

O produtor tem alguma variável que aponta diretamente para um consumidor? Os consumidores têm alguma variável que aponta para o produtor?

> _Resposta:_

Como eles se coordenam, então?

> _Resposta:_

### 1.5 Experimentos dirigidos

**Experimento 1 — Remover consumidor-b:**

O que aconteceu com as tarefas após comentar o `consumidor-b`? Alguma tarefa se perdeu?

> _Observado:_

O que isso revela sobre o papel do espaço de tuplas em relação ao acoplamento temporal (produtor e consumidor precisam estar ativos ao mesmo tempo)?

> _Resposta:_

**Experimento 2 — Produtor rápido, consumidor lento:**

Descreva o estado do espaço enquanto o produtor publica todas as tarefas antes que os consumidores as retirem:

> _Observado:_

O espaço de tuplas se comportou como um _buffer_? Explique.

> _Resposta:_

---

## Nível 2 — Modificar

### 2.1 Modificação A — Prioridade de tarefas

Descreva as mudanças que você fez no `consumidor.py` para dar suporte a prioridades:

> _O que foi alterado e por quê:_

Cole um trecho dos logs que evidencia que as tarefas de alta prioridade foram processadas antes das de baixa prioridade:

```
(cole o trecho de log aqui)
```

Como você lidou com a ausência de um `IN` com timeout no protocolo Linda? Que solução adotou?

> _Resposta:_

### 2.2 Modificação B — Serviço monitor

Por que você usou `RD` e não `IN` no monitor?

> _Resposta:_

Como você resolveu (ou tentou resolver) o problema de contar tuplas usando apenas `RD`? O que ficou faltando?

> _Resposta:_

Cole o código do `monitor/monitor.py` que você criou:

```python

```

---

## Conexão com sistemas modernos

Cite dois sistemas de mensageria modernos que implementam o padrão de desacoplamento espacial observado nesta atividade:

> _Resposta:_

Qual operação do espaço de tuplas é análoga ao "publish" nesses sistemas?

> _Resposta:_

Qual a principal diferença prática entre o espaço de tuplas que você implementou e um broker como o RabbitMQ ou o Kafka?

> _Resposta:_

---

## Observações livres

_(Comportamentos inesperados, erros encontrados, dificuldades técnicas)_

>

---

## Dúvida para a próxima aula

_(Formule uma pergunta substantiva que surgiu durante a atividade)_

>
