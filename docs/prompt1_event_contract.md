# Prompt 1 — Contrato Público de Eventos e Fluxo Lógico

Este documento consolida o formalismo de eventos de domínio implementado no Prompt 1.

## Contrato Público (`domain.events`)

Eventos exportados pelo pacote:

- `DomainEvent` (abstrato)
- `WorkloadSubmittedEvent`
- `WorkloadDeliveredEvent`
- `TaskStartedEvent`
- `TaskCompletedEvent`

Leis garantidas no nível de objeto:

- **L1 Imutabilidade estrutural:** eventos são frozen e não podem ser alterados após criação.
- **L2 Identidade única automática:** `event_id` usa UUID com geração automática.
- **L3 Ordem temporal consistente:** eventos são comparáveis por `timestamp`.
- **L4 Igualdade por identidade:** igualdade/hashing baseados apenas em `event_id`.
- **L5 Representação informativa:** `repr` contém tipo do evento, `event_id` e `timestamp`.

Validações adicionais de robustez:

- `event_id` deve ser `UUID`.
- `timestamp` deve ser escalar real e finito.

## Fluxo lógico de eventos (domínio puro)

Abaixo, o mapeamento evento → produtor lógico → consumidor lógico no domínio.

| Evento | Produtor lógico | Consumidor lógico | Papel causal |
|---|---|---|---|
| `WorkloadSubmittedEvent` | Adaptador de entrada (telemetria/fila) | Orquestrador de aplicação (`DataCenterTwin`) | Marca entrada de nova carga no sistema |
| `WorkloadDeliveredEvent` | Módulo de rede do domínio | Módulo de computação / escalonamento | Marca disponibilidade de workload no destino |
| `TaskStartedEvent` | Escalonador/compute domain | Agregados de estado e contratos temporais | Marca início de execução |
| `TaskCompletedEvent` | Executor/compute domain | Agregados de estado, contratos estatísticos e snapshots | Marca fim de execução e fechamento causal |

> Observação arquitetural: este fluxo é intencionalmente independente de Kafka ou qualquer middleware, preservando o núcleo hexagonal puro.

## Critério de prontidão do Prompt 1

Prompt 1 é considerado concluído quando:

1. classes de evento existem com contrato formal;
2. pacote público `domain.events` exporta o conjunto canônico;
3. testes L1–L5 passam de forma determinística;
4. o fluxo causal lógico está explicitado para orientar a próxima etapa (event bus determinístico/replay).
