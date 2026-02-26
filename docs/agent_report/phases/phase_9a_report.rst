Phase 9A Report — Kafka Streaming Ingestion Adapter + Unified Stack Compose
============================================================================

1. Phase Overview
-----------------

- **Phase number:** 9A
- **Date:** 2026-02-26
- **Commit reference (if available):** ``69b4f1a``
- **Related roadmap section:** :doc:`../../engineering/implementation_roadmap`

2. Architectural Scope
----------------------

- **Components introduced:**

  - Streaming infrastructure adapter package under
    ``src/digital_twin/infrastructure/streaming``:

    - ``kafka_config.py`` (runtime settings from environment);
    - ``message_schema.py`` (canonical telemetry contract validation);
    - ``normalizer.py`` (Kafka -> ``DomainEvent`` normalization);
    - ``kafka_consumer.py`` (single-threaded consume/ingest/commit loop + DLQ path);
    - ``kafka_producer.py`` (optional control-topic producer);
    - package export module ``__init__.py``.

  - Unified local stack compose file ``docker-compose.stack.yml`` with
    PostgreSQL, ZooKeeper, Kafka, Kafka UI and pgAdmin.

  - Stack environment example ``.env.stack.example``.

  - Streaming test suite in ``tests/streaming`` for schema, mapping,
    idempotency contract, ordering and DLQ behavior.

- **Documents modified:**

  - ``docs/engineering/kafka_protocol.rst`` (new protocol/runbook);
  - ``docs/engineering/index.rst`` (toctree inclusion);
  - ``docs/architecture/evolution_history.rst`` (Phase 9A registration).

- **Contracts affected:**

  - Kafka telemetry message schema requires:

    - ``stream_id``
    - ``source``
    - ``source_time_utc`` (RFC3339)
    - ``event_type``
    - ``payload`` (JSON object)

  - ``ingest_id`` must be UUID when provided; if absent, generated at
    ingestion boundary as metadata token.

  - Event payload required fields are validated per known ``event_type`` before
    normalization.

  - Consumer processing policy:

    - single-threaded sequential handling;
    - consume -> normalize -> ``DataCenterTwin.ingest_event``;
    - offset commit after successful handling;
    - on ``VersionConflictError``: stop and raise;
    - on validation/transition failure: publish DLQ and commit;
    - duplicate ingest is handled by idempotency signal from persistence path.

- **Data structures introduced:**

  - ``KafkaSettings``
  - ``KafkaTelemetryMessage``
  - ``KafkaValidationError``
  - ``KafkaMessageContext``
  - observational metadata key ``_ingest_observation``

Reference architecture baseline: :doc:`../../architecture/system_blueprint`.

3. Formal Model Impact
----------------------

- **Impact on** :math:`(X, E, H, V, \mathcal{I}, \mathcal{O})`:

  - no change in domain transition semantics :math:`H` and validator :math:`V`;
  - changes are infrastructure-bound on ingestion side of event space :math:`E`;
  - inference :math:`\mathcal{I}` and optimization :math:`\mathcal{O}` remain
    behaviorally unchanged.

- **State extensions (if any):** no extension to domain state :math:`X`.

- **Invariant extensions (if any):**

  - stream-level idempotency remains keyed by ``(stream_id, ingest_id)`` in DB;
  - replay ordering remains by ``event_log.seq ASC``;
  - ingest adapter keeps single-message sequential application order;
  - no direct domain mutation path was added outside
    ``DataCenterTwin.ingest_event``.

4. Determinism Verification
---------------------------

- **Replay tests executed:**

  - ``PYTHONPATH=src pytest -q tests/streaming/test_message_schema_validation.py tests/streaming/test_normalizer_mapping.py tests/streaming/test_kafka_to_db_idempotency.py tests/streaming/test_kafka_ordering_single_partition.py tests/streaming/test_kafka_dlq_on_invalid_message.py``

- **Results:**

  - streaming suite executed with ``5 passed, 3 skipped``;
  - skips are explicit for kafka-marked tests when ``KAFKA_BROKERS`` is not
    configured, preserving deterministic CI behavior;
  - idempotency path validated by duplicate ingest token test contract;
  - per-partition ordering behavior validated by sequential consume contract test;
  - invalid-message path validated to route to DLQ without consumer-loop crash.

- **Edge cases observed:**

  - when Kafka runtime is unavailable locally, integration-marked tests are
    skipped by design with clear reason.

Determinism claims must align with :doc:`../../engineering/determinism_and_replay`.

5. Performance Validation
-------------------------

- **Throughput:** no dedicated throughput benchmark executed in this phase report.
- **p95 / p99 latency:** not benchmarked; values remain TBD for Phase 9A runtime envelope.
- **Memory usage:** no measured delta reported; domain memory model unchanged.
- **Snapshot cost:** unchanged by this phase; snapshot path remains in-domain,
  with persistence ordering governed by DB event log semantics.
- **Inference latency (if applicable):** unchanged.
- **Optimization latency (if applicable):** unchanged.

Performance acceptance must reference :doc:`../../engineering/performance_budget`.

6. Load Testing Results
-----------------------

- **Load profile used:** not executed in this phase report.
- **Duration:** not executed.
- **Failure conditions observed:** not executed.
- **Replay validation result:** deterministic ingestion contracts validated in
  focused streaming tests; full runtime load profile remains pending.

Use protocol alignment with :doc:`../../engineering/local_load_testing_protocol`.

7. Contract Validation
----------------------

- **Invariants tested:**

  - telemetry schema validation rejects malformed UUID and missing required
    payload fields;
  - normalization maps Kafka contract to canonical ``DomainEvent`` while
    preserving observational metadata as side-channel payload data;
  - duplicate ingest token path is treated as idempotent skip contract;
  - sequential ordering is preserved for single-partition input sequence;
  - invalid payload path is routed to DLQ and offset is committed.

- **Violations found:** no unresolved violations in executed test subset.

- **Resolution steps:**

  - persistence idempotency signal is propagated through ``DataCenterTwin`` via
    ``last_append_result`` and rollback on duplicate append result;
  - consumer adapter failure branches were constrained to deterministic
    operational handling (raise on version conflict, DLQ on validation errors).

8. Failure Propagation Observations
-----------------------------------

- **H failures:** transition ``ValueError`` surfaces in adapter and is routed to DLQ.
- **V failures:** validator failures follow the same DLQ path in consumer policy.
- **Inference failures:** unchanged (not in Phase 9A scope).
- **Optimization failures:** unchanged (not in Phase 9A scope).
- **Recovery behavior:** unchanged baseline: recover via latest snapshot + tail
  replay ordered by ``seq ASC``.

9. Architectural Trade-offs
---------------------------

- **Performance vs clarity:** single-threaded consumer model favors deterministic
  clarity over maximal ingestion throughput.
- **Memory vs speed:** no major memory trade introduced; observational metadata
  in payload increases event size slightly while improving auditability.
- **Determinism safeguards:** strict schema checks, sequential processing,
  idempotent ingest token, and conflict-stop policy on stream divergence.
- **Simplifications made:** Phase 9A keeps producer path optional and focuses on
  telemetry ingestion adapter semantics.

10. Known Limitations
---------------------

- **Technical debt introduced:** no real Kafka broker integration benchmark is
  attached to this report.
- **Performance ceilings:** single-consumer-thread design may limit peak throughput.
- **Unresolved risks:** production rollout needs operational tuning for
  partitions, consumer groups and DLQ monitoring/retention policy.

11. Phase Gate Decision
-----------------------

- **Passed with warnings**

Warnings:

- end-to-end load/performance envelope for Kafka-backed ingestion remains pending
  dedicated runtime campaign.

12. Next Phase Preparation
--------------------------

- **Dependencies satisfied:** canonical telemetry contract, normalization,
  adapter control flow, unified stack compose, and baseline streaming tests are in place.
- **Risks for next phase:** throughput scaling and observability hardening for
  Kafka runtime operations.
- **Refactoring required before next phase:** add broker-backed integration test
  execution in CI (or reproducible local profile) and export ingestion adapter
  metrics into unified metrics architecture.

Required Cross-References
-------------------------

This report aligns conclusions with:

- :doc:`../../architecture/system_blueprint`
- :doc:`../../engineering/performance_budget`
- :doc:`../../engineering/implementation_roadmap`
- :doc:`../../engineering/local_load_testing_protocol`
- :doc:`../../engineering/internal_metrics_architecture`
- :doc:`../../engineering/determinism_and_replay`
