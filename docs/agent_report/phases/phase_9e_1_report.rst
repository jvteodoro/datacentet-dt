Phase 9E.1 Report — HTTP Ingestion Load Testing + Locust Hyperscale Input Simulation
======================================================================================

1. Phase Overview
-----------------

- **Phase number:** 9E.1
- **Date:** 2026-02-26
- **Commit reference (if available):** ``ffb0c55``
- **Related roadmap section:** :doc:`../../engineering/implementation_roadmap`

2. Architectural Scope
----------------------

- **Components introduced:**

  - HTTP ingestion gateway and runner:
    ``src/digital_twin/presentation/ingestion_http_api.py`` and
    ``src/digital_twin/presentation/ingestion_http_runner.py``.
  - Shared ingestion schema and normalizer:
    ``src/digital_twin/infrastructure/ingestion/message_contract.py`` and
    ``src/digital_twin/infrastructure/ingestion/normalize.py``.
  - Kafka normalization factorization through shared ingestion path:
    ``src/digital_twin/infrastructure/streaming/message_schema.py`` and
    ``src/digital_twin/infrastructure/streaming/normalizer.py``.
  - Coordinator extension for pre-normalized event ingestion:
    ``src/digital_twin/infrastructure/streaming/coordinator.py``.
  - Deterministic Locust ingestion suite:
    ``load_testing/locust_ingest/``.

- **Documents modified:**

  - ``docs/engineering/local_load_testing_ingestion_http.rst``
  - ``docs/engineering/load_testing_strategy_http_vs_kafka.rst``
  - ``docs/engineering/index.rst``
  - ``docs/engineering/performance_budget.rst``
  - ``docs/architecture/evolution_history.rst``

- **Contracts affected:**

  - Shared telemetry message contract now explicit for HTTP and Kafka paths.
  - Ingestion outcome contract exposed over HTTP: ``APPLIED``, ``DUPLICATE``,
    ``DLQ``, ``VERSION_CONFLICT``.
  - Idempotency policy reinforced by requiring client ``ingest_id`` for load
    tests by default.

- **Data structures introduced:**

  - ``TelemetryMessage``
  - ``HTTPIngestionMetrics``
  - ``IngestProfileSpec``
  - ``RuntimeConfig``
  - ``SeededTrafficGenerator``

Reference architecture baseline: :doc:`../../architecture/system_blueprint`.

3. Formal Model Impact
----------------------

- **Impact on** :math:`(X, E, H, V, \mathcal{I}, \mathcal{O})`:

  - :math:`E` gains an additional transport entry path (HTTP) that maps to the
    same logical telemetry event contract used by Kafka.
  - :math:`H` and :math:`V` semantics are preserved; no mutation semantics were
    moved outside canonical transition and validation operators.
  - :math:`\mathcal{O}` is extended with ingestion gateway latency and status
    distribution metrics as side-channel telemetry.

- **State extensions (if any):**

  - No domain state extension was introduced in the core twin state.
  - Stream coordinator operational bookkeeping remains bounded and consistent
    with existing eviction policy.

- **Invariant extensions (if any):**

  - Deterministic batch ordering policy for HTTP batch ingestion documented as
    ``sorted(source_time_utc, ingest_id)``.
  - Client-provided ``ingest_id`` requirement for replay-comparable load tests.

4. Determinism Verification
---------------------------

- **Replay tests executed:**

  - ``pytest -q tests/streaming/test_normalizer_mapping.py``
  - ``pytest -q tests/infrastructure/test_shared_normalizer_equivalence.py``
  - ``pytest -q tests/streaming/test_message_schema_validation.py``

- **Results:**

  - Shared and Kafka normalization paths are equivalent for identical message
    inputs under deterministic metadata mapping.
  - Message contract enforcement is deterministic for required fields and UUID
    parsing behavior.

- **Edge cases observed:**

  - Missing ``ingest_id`` under ``require_ingest_id=True`` maps to explicit
    HTTP ``DLQ`` response path.
  - Batch payload item ordering is deterministic after explicit sort.

Determinism claims align with :doc:`../../engineering/determinism_and_replay`.

5. Performance Validation
-------------------------

- **Throughput:** Not measured in this implementation phase.
- **p95 / p99 latency:** Not measured; placeholders documented in
  :doc:`../../engineering/performance_budget`.
- **Memory usage:** Not measured.
- **Snapshot cost:** Not measured.
- **Inference latency (if applicable):** Not applicable.
- **Optimization latency (if applicable):** Not applicable.

Performance acceptance references
:doc:`../../engineering/performance_budget`.

6. Load Testing Results
-----------------------

- **Load profile used:**

  - Profiles were implemented and unit-validated:
    ``steady_poisson_users``, ``burst_pareto_users``, ``multi_stream_scale``,
    ``tick_heavy_infra``, and ``mixed_with_flows``.

- **Duration:** No full Locust runtime campaign executed in this phase report.
- **Failure conditions observed:** None from unit-level validation.
- **Replay validation result:** Deterministic profile generation verified for
  equal seeds in unit tests.

Protocol alignment: :doc:`../../engineering/local_load_testing_protocol`.

7. Contract Validation
----------------------

- **Invariants tested:**

  - Schema enforcement for ingestion messages.
  - Deterministic response serialization and key ordering.
  - Shared normalizer equivalence with Kafka normalizer.
  - Seed-deterministic profile event generation.

- **Violations found:** No contract violations in executed tests.

- **Resolution steps:**

  - Test harness for HTTP ingestion was configured to use in-memory
    ``DataCenterTwin`` construction in order to avoid external DB dependency
    during contract validation.

8. Failure Propagation Observations
-----------------------------------

- **H failures:** Validation failures are mapped to explicit ``DLQ`` outcome
  payloads over HTTP with status 400.
- **V failures:** Version conflict path mapped to ``VERSION_CONFLICT`` with
  status 409.
- **Inference failures:** Not applicable in this phase.
- **Optimization failures:** Not applicable in this phase.
- **Recovery behavior:** Existing persistence/recovery pathway unchanged;
  no replay semantics changes introduced.

9. Architectural Trade-offs
---------------------------

- **Performance vs clarity:**

  - Shared normalization removes duplication and clarifies semantic equivalence
    between HTTP and Kafka ingestion paths.

- **Memory vs speed:**

  - Additional HTTP-side instrumentation stores request latency samples for
    local operational analysis; this favors local observability clarity.

- **Determinism safeguards:**

  - Explicit seeded RNG strategy in Locust profile generation.
  - Explicit deterministic ordering rule in batch ingestion handling.

- **Simplifications made:**

  - HTTP implementation remains lightweight (stdlib server) to minimize
    framework overhead and preserve local reproducibility.

10. Known Limitations
---------------------

- **Technical debt introduced:**

  - Ingestion campaign thresholds remain placeholders until empirical runs are
    executed and baselined.

- **Performance ceilings:**

  - HTTP-only phase does not expose broker/partition/rebalance ceilings.

- **Unresolved risks:**

  - Comparative HTTP-vs-Kafka bottleneck attribution depends on subsequent
    Kafka load campaign with equivalent workload semantics.

11. Phase Gate Decision
-----------------------

- **Passed with warnings**

Warnings are limited to absence of full measured load campaign data in this
report; implementation and unit validation gates were satisfied.

12. Next Phase Preparation
--------------------------

- **Dependencies satisfied:**

  - Shared ingestion contract in place for HTTP/Kafka parity.
  - Deterministic profile generator available for workload replayability.

- **Risks for next phase:**

  - Need empirical Locust and Kafka campaign outputs (p50/p95/p99,
    throughput, error-rate, and resource envelope) before closing
    performance-budget placeholders.

- **Refactoring required before next phase:**

  - Minimal; primary work is execution/analysis of load campaigns and
    alignment to acceptance thresholds.

Required Cross-References
-------------------------

- :doc:`../../architecture/system_blueprint`
- :doc:`../../engineering/performance_budget`
- :doc:`../../engineering/implementation_roadmap`
- :doc:`../../engineering/local_load_testing_protocol`
- :doc:`../../engineering/internal_metrics_architecture`
- :doc:`../../engineering/determinism_and_replay`
