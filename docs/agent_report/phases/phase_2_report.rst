Phase 2 Report
==============

1. Phase Overview
-----------------

- **Phase number:** 2
- **Date:** 2026-02-24
- **Commit reference (if available):** c7e268b
- **Related roadmap section:** :doc:`../../engineering/implementation_roadmap`

2. Architectural Scope
----------------------

- **Components introduced:**

  - ``src/digital_twin/domain/state.py``
  - ``src/digital_twin/domain/transition.py``
  - ``src/digital_twin/domain/validation.py``
  - ``src/digital_twin/domain/snapshot.py``
  - ``src/digital_twin/domain/twin.py``
  - ``tests/domain/test_network_determinism.py``
  - ``tests/domain/test_flow_conservation.py``
  - ``tests/domain/test_capacity_violation.py``
  - ``tests/domain/test_no_global_scan_behavior.py``
  - ``tests/domain/test_no_full_copy_complexity.py``

- **Documents modified:**

  - ``docs/agent_report/phases/phase_2_report.rst``

- **Contracts affected:**

  - Expansão determinística de :math:`(X, E, H, V)` para modelo de rede em nível de fluxo.
  - Ordem canônica de execução preservada: normalize :math:`\rightarrow` H :math:`\rightarrow` V :math:`\rightarrow` commit :math:`\rightarrow` persist :math:`\rightarrow` snapshot.
  - Sem alterações em semântica de métricas e mecanismo de replay.

- **Data structures introduced:**

  - ``FlowRecord(src_idx, dst_idx, path, rate, remaining_size)``
  - ``NetworkTopology(node_index, reverse_node_index, adjacency, link_capacity, link_index)``
  - ``TwinState(topology, link_backlog, active_flows, version_counter, event_counter)``
  - ``TransitionCandidate(state, modified_link_indices, modified_flow_ids)``

Reference architecture baseline: :doc:`../../architecture/system_blueprint`.

3. Formal Model Impact
----------------------

- **Impact on** :math:`(X, E, H, V, \mathcal{I}, \mathcal{O})`:

  - ``X``: estado separado em topologia (estrutural) e dinâmica (backlog/flows).
  - ``E``: suporte explícito a eventos ``AddNode``, ``AddLink``, ``FlowStarted`` e ``FlowEnded``.
  - ``H``: transições locais por entidade afetada, com copy-on-write para backlog/flows em eventos de fluxo.
  - ``V``: validação estendida sobre links/flows modificados, sem varredura global.
  - ``\mathcal{I}`` e ``\mathcal{O}``: sem expansão nesta fase.

- **State extensions (if any):**

  - Topologia movida para ``state.topology`` (``node_index``, ``reverse_node_index``, ``adjacency``, ``link_capacity``, ``link_index``).
  - Estado dinâmico em ``link_backlog`` e ``active_flows``.
  - Metadados de transição ``modified_*`` removidos do estado persistido e mantidos em ``TransitionCandidate``.

- **Invariant extensions (if any):**

  - Para cada link modificado: ``backlog >= 0`` e ``backlog <= capacity``.
  - Para cada fluxo modificado e ativo: ``rate >= 0`` e ``remaining_size >= 0``.

4. Determinism Verification
---------------------------

- **Replay tests executed:**

  - ``PYTHONPATH=src pytest -q tests/domain``

- **Results:**

  - Determinismo preservado para mesma condição inicial e mesma sequência ordenada de eventos.
  - Igualdade de replay confirmada para topologia, backlog de links, fluxos ativos, snapshot e event log.
  - Falha de validação por capacidade impede commit/persistência, preservando estado/snapshot/log anteriores.

- **Edge cases observed:**

  - ``FlowStarted`` com caminho inválido ou links inexistentes é rejeitado em ``H``.
  - ``FlowEnded`` para fluxo inexistente é rejeitado em ``H``.
  - Invariantes são avaliados após construção do estado candidato e antes de commit.

Determinism claims must align with :doc:`../../engineering/determinism_and_replay`.

5. Performance Validation
-------------------------

- **Throughput:** Não medido por benchmark dedicado nesta fase.
- **p95 / p99 latency:** Não medido por benchmark dedicado nesta fase.
- **Memory usage:** Não medido por benchmark dedicado nesta fase.
- **Snapshot cost:** Cópia imutável de ``link_backlog`` via ``tuple(state.link_backlog)``.
- **Inference latency (if applicable):** Não aplicável (sem inferência na Phase 2).
- **Optimization latency (if applicable):** Não aplicável (sem otimização na Phase 2).

Performance acceptance must reference :doc:`../../engineering/performance_budget`.

6. Load Testing Results
-----------------------

- **Load profile used:** Não executado nesta fase.
- **Duration:** Não executado nesta fase.
- **Failure conditions observed:** Não executado nesta fase.
- **Replay validation result:** Replay funcional validado por suíte de testes de domínio.

Use protocol alignment with :doc:`../../engineering/local_load_testing_protocol`.

7. Contract Validation
----------------------

- **Invariants tested:**

  - Conservação local de backlog por caminho de fluxo.
  - Limite de capacidade por link.
  - Não-negatividade de backlog/rate/remaining_size.
  - Ordem canônica de ingestão e validação pré-commit.

- **Violations found:**

  - Violação intencional de capacidade reproduzida e corretamente bloqueada sem commit.

- **Resolution steps:**

  - Validação baseada em ``TransitionCandidate`` para links/flows modificados.
  - Testes de identidade estrutural para garantir ausência de full-copy em eventos de fluxo.

8. Failure Propagation Observations
-----------------------------------

- **H failures:** Erros determinísticos para nó/link/fluxo desconhecido e inconsistência de caminho.
- **V failures:** Exceção de validação bloqueia commit e persistência do evento.
- **Inference failures:** Não aplicável.
- **Optimization failures:** Não aplicável.
- **Recovery behavior:** Replay determinístico reconstrói estado final idêntico.

9. Architectural Trade-offs
---------------------------

- **Performance vs clarity:**

  - Separação explícita ``NetworkTopology`` + estado dinâmico reduz cópias globais em eventos de fluxo.

- **Memory vs speed:**

  - Copy-on-write para ``link_backlog`` e ``active_flows`` apenas quando há modificação.

- **Determinism safeguards:**

  - Ordem de inserção de nós baseada em sequência de eventos.
  - Ausência de iteração sobre conjuntos não ordenados.
  - Atualizações estritamente locais aos links do caminho.

- **Simplifications made:**

  - Modelo de rede mínimo (sem cluster de compute, inferência ou otimização).
  - Sem persistência externa.

10. Known Limitations
---------------------

- **Technical debt introduced:**

  - ``TransitionCandidate`` adiciona um tipo intermediário na API interna de ingestão.

- **Performance ceilings:**

  - Não há envelope quantitativo de throughput/latência com carga elevada.

- **Unresolved risks:**

  - Necessário complementar benchmark formal antes de gate com critérios de performance estritos.

11. Phase Gate Decision
-----------------------

- **Passed with warnings**

Warnings restritos à ausência de benchmark dedicado de performance e ausência de teste de carga protocolado, apesar de validação funcional/determinística completa no escopo de Phase 2.

12. Next Phase Preparation
--------------------------

- **Dependencies satisfied:**

  - Núcleo determinístico com topologia estrutural e dinâmica copy-on-write pronto para extensões futuras.

- **Risks for next phase:**

  - Evolução do modelo pode exigir estrutura dinâmica ainda mais especializada para escalas extremas.

- **Refactoring required before next phase:**

  - Preservar ordem canônica de ingestão e semântica de replay/métricas.
  - Manter complexidade por evento proporcional ao número de entidades afetadas.

Required Cross-References
-------------------------

This report aligns conclusions with:

- :doc:`../../architecture/system_blueprint`
- :doc:`../../engineering/performance_budget`
- :doc:`../../engineering/implementation_roadmap`
- :doc:`../../engineering/local_load_testing_protocol`
- :doc:`../../engineering/internal_metrics_architecture`
- :doc:`../../engineering/determinism_and_replay`


Revision Notes
--------------

- **2026-02-24 (phase 2.1 update):** report updated to reflect structural efficiency refactor with ``NetworkTopology`` separation, ``TransitionCandidate`` validation-local metadata, copy-on-write behavior for flow events, and new no-full-copy tests.
