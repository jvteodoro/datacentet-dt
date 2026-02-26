Implementation Roadmap
=======================

1. Purpose
----------

This roadmap defines the disciplined, performance-aware implementation plan
for the hyperscale Data Center Digital Twin.

The system is formally defined as:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

The roadmap ensures:

- Deterministic correctness
- Contract enforcement
- Hyperscale scalability
- Load resilience
- Scientific reproducibility

Load testing is integrated as a mandatory validation layer.

---

2. Engineering Principles
--------------------------

The implementation must follow:

1. Determinism first.
2. Contracts before optimization.
3. Sparse updates only.
4. No global scans.
5. Replay must always succeed.
6. Performance regressions block release.

---

3. Phase 0 — Performance Budget Definition
-------------------------------------------

Before implementation, define quantitative targets:

- Target events/sec ingestion
- Target maximum active flows
- Target maximum active workloads
- Target p95 and p99 event latency
- Target snapshot latency
- Target inference latency window
- Target optimization latency window
- Target memory per 1M flows

No phase may proceed without measurable performance goals.

---

4. Phase 1 — Core Domain Skeleton
----------------------------------

Objectives:

- Event base class
- InternalEventBus
- Deterministic event loop
- DataCenterTwin core
- Basic empty snapshot

Mandatory Tests:

- Unit tests
- Replay tests
- Determinism tests

Gate:

Replay must produce identical state across runs.

---

5. Phase 2 — Flow-Level Network Engine
---------------------------------------

Objectives:

- Immutable topology structure
- Flat link arrays
- Sparse flow tracking
- Flow conservation update rule

Mandatory Tests:

- Network contract tests
- Replay tests
- Micro load test (Locust local)

Gate:

Per-event latency must not scale with :math:`|V|` or :math:`|E|`.

---

6. Phase 3 — Compute Cluster Engine
------------------------------------

Objectives:

- Flat server arrays
- Sparse workload tracking
- CPU and memory bounds enforcement

Mandatory Tests:

- Compute contract tests
- Replay tests
- Micro load test

Gate:

No global per-server scan allowed.

---

7. Phase 4 — Flow-Level Validation Operator
--------------------------------------------

Objectives:

- Link capacity constraints
- CPU capacity constraints
- Memory bounds
- Flow conservation
- Temporal ordering enforcement

Mandatory Tests:

- Explicit violation tests
- Load test under contract validation

Gate:

Invalid state must halt execution.

---

8. Phase 5 — Snapshot System
-----------------------------

Objectives:

- Immutable snapshot view
- Delta-based mutation tracking
- Snapshot equality logic

Mandatory Tests:

- Snapshot immutability
- Replay equivalence
- Snapshot under load

Gate:

Snapshot must not scale with full topology size.

---

9. Phase 6 — Synthetic Mode
----------------------------

Objectives:

- Synthetic event generator
- Burst workload generator
- Link failure simulation

Mandatory Tests:

- Burst load test (Locust)
- Flow churn test
- Replay after stress

Gate:

System must remain deterministic under burst.

---

10. Phase 7 — Persistence Layer
--------------------------------

Objectives:

- Append-only event store
- Snapshot persistence
- Recovery procedure

Mandatory Tests:

- Replay from persisted logs
- Recovery under load
- Load test with persistence active

Gate:

Recovered state must equal live state.

---

11. Phase 8 — Inference Layer
------------------------------

Objectives:

- InferenceStrategy interface
- Simple deterministic inference implementation
- Parameter validation rules

Mandatory Tests:

- Replay with inference active
- Stability under window load
- Deterministic parameter updates

Gate:

Inference must not violate contracts.

---

12. Phase 9 — Optimization Layer
---------------------------------

Objectives:

- OptimizationStrategy interface
- Deterministic congestion-aware strategy
- Control events reinjected via ingestion

Mandatory Tests:

- Replay with optimization active
- Load test under congestion
- Deterministic action proposal

Gate:

Optimization must never mutate domain directly.

---

13. Phase 10 — Full System Load Validation
-------------------------------------------

Objectives:

- Kafka ingestion
- Inference active
- Optimization active
- Persistence active
- Snapshot active

Mandatory Load Tests:

- Steady 10k events/sec
- Burst 100k events/sec
- Flow churn stress
- Failure injection
- Replay validation after load

Gate:

No replay mismatch.
No contract violation.
Latency within defined budget.

---

14. Load Testing Integration (Locust)
--------------------------------------

Load testing is mandatory in:

- Phase 2 onward (micro load tests)
- Phase 6 onward (burst tests)
- Phase 10 (system readiness benchmark)

Performance Metrics:

- event_processing_latency
- p95_latency
- p99_latency
- snapshot_latency
- inference_latency
- optimization_latency
- memory_usage
- active_flows_count
- active_workloads_count

Failure Conditions:

- Latency grows with :math:`|V|`
- Memory grows unbounded
- Replay mismatch
- Contract violation
- Inference divergence
- Optimization instability

---

15. Milestone Targets
----------------------

Milestone A:
    10k flows stable replay

Milestone B:
    100k links sparse update

Milestone C:
    1M active flows no global scan

Milestone D:
    Inference window < defined threshold

Milestone E:
    Optimization window < defined threshold

Milestone F:
    Deterministic replay under sustained load

---

16. CI/CD Requirements
-----------------------

Pipeline must include:

- Unit tests
- Contract tests
- Replay tests
- Micro load tests
- Weekly performance regression test

Performance regression blocks merge.

---

17. Definition of Done
-----------------------

The system is considered production-ready when:

- Deterministic replay proven
- Performance budget satisfied
- No global scans detected
- Contracts validated under load
- Persistence recovery verified
- Inference stable
- Optimization deterministic

---

18. Scientific Validation Stage
-------------------------------

Before publication or deployment:

- Record event logs
- Run burst stress
- Run drift scenarios
- Run failure injection
- Replay and compare state

Reproducibility is mandatory.

---

19. Summary
-----------

This roadmap ensures:

- Controlled architectural growth
- Hyperscale scalability
- Deterministic integrity
- Load resilience
- Scientific reproducibility

No phase may be skipped.

Load validation is not optional.

Architecture Alignment Note
---------------------------

This document conforms to the canonical model:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

It preserves the determinism rule: identical initial state :math:`X_0`, identical ordered event sequence :math:`(e_1, \dots, e_n)`, identical initial parameter vector :math:`\theta_0`, and identical inference/optimization seeds must produce identical :math:`X_n`, validation outcomes, :math:`\theta_n`, and control actions :math:`u_n`.



Replay Semantics Clarification
------------------------------

Replay mode must reapply events through ingestion :math:`\rightarrow H \rightarrow V`, then execute deterministic inference and deterministic optimization, and reproduce emitted control events.

If inference/optimization are intentionally excluded, the run must be labeled limited replay mode and is valid only for domain-state determinism checks.

Validation and persistence ordering is mandatory per event:

::

    normalize -> H -> V -> persist -> snapshot update -> inference window update

If :math:`V(X_{t+1})` is not valid, the event must not be persisted and must not update snapshot or inference windows.

Phase 2.2 Note — Hyperscale Structural Refactor
------------------------------------------------

Phase 2.2 introduces in-place dynamic updates with transition-local rollback in the
single-threaded deterministic domain core.

Design target and verification objective for flow events:

- strict :math:`O(path\_length)` transition work for ``FlowStarted`` and ``FlowEnded``
- no full dynamic-container copy in flow event paths
- validation restricted to modified entities


DB Adapter Envelope (initial)
-----------------------------

This envelope applies to PostgreSQL persistence adapters in infrastructure
(``EventStorePG`` and ``SnapshotStorePG``).

- **Append latency targets (single append):**

  - p95: **TBD** (measure in environment-specific load tests)
  - p99: **TBD** (measure in environment-specific load tests)

- **Sustained append rate target:** **TBD** events/s (to be fixed after baseline load campaign).
- **Replay ordering constraint:** all replay reads must remain ``ORDER BY seq ASC``.
- **Batching guidance:** prefer bounded deterministic batches when ingest pressure is high;
  batch append must remain atomic and preserve caller order.
- **Pooling guidance:** use connection pooling when ``psycopg_pool`` is available; fallback
  connection factory is allowed with explicit limitation on throughput.


16. Phase 9C Streaming Partition Sizing Guidance
------------------------------------------------

Initial targets (to be refined with runtime benchmarks):

- **Max streams per consumer instance (initial):** 50–200 active streams.
- **Expected per-stream ingest rate (initial):** 50–500 events/s.
- **Partition count guidance:**

  - choose partitions >= active high-throughput streams requiring parallelism;
  - maintain headroom for rebalance and lag recovery;
  - keep per-partition load below the p95 ingest latency envelope.

These are initial planning values and remain **TBD** for production finalization
after dedicated load validation.


17. Phase 9C.1 Operational Hardening Targets
--------------------------------------------

Initial operating guidance (subject to benchmark refinement):

- **max_active_streams** recommended range per consumer process: 200–2000.
- **stream_ttl_seconds** default guidance: 300–1800 seconds depending on
  stream burstiness and recovery tolerance.
- **acceptable eviction-rate threshold (steady state):** < 5% of active streams
  per minute under normal load; sustained higher rates indicate partitioning or
  capacity tuning requirements.

All targets are initial and remain TBD for production calibration after
dedicated load campaigns.
