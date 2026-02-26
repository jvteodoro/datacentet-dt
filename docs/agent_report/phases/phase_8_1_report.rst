Phase 8.1 Report — Persistence Hardening and Performance Envelope
==================================================================

1. Phase Overview
-----------------

- **Phase number:** 8.1
- **Date:** 2026-02-26
- **Commit reference (if available):** ``04f3813``
- **Related roadmap section:** :doc:`../../engineering/implementation_roadmap`

2. Architectural Scope
----------------------

- **Components introduced:** hardening migration ``0002_hardening.sql``, append result/conflict semantics in ``EventStorePG``, snapshot pruning in ``SnapshotStorePG``, DB adapter metrics side-channel, and connection factory with optional pooling.
- **Documents modified:** ``docs/engineering/real_db_protocol.rst``, ``docs/engineering/performance_budget.rst``, ``docs/architecture/evolution_history.rst``.
- **Contracts affected:** stream-level uniqueness (logical version + ingest id), deterministic replay ordering by ``seq ASC``, explicit idempotency signaling, snapshot pruning policy as operational compaction only.
- **Data structures introduced:** ``AppendResult``, ``VersionConflictError``, ``AppendRequest``, ``DBAdapterMetrics``.

Reference architecture baseline: :doc:`../../architecture/system_blueprint`.

3. Formal Model Impact
----------------------

- **Impact on** :math:`(X, E, H, V, \mathcal{I}, \mathcal{O})`: no change to domain transition semantics :math:`H` or validator :math:`V`; persistence hardening affects storage integrity and adapter behavior for event space :math:`E` only.
- **State extensions (if any):** no extension to domain state ``X``.
- **Invariant extensions (if any):**

  - ``UNIQUE(stream_id, version_counter)`` in ``event_log``;
  - ``UNIQUE(stream_id, ingest_id)`` in ``event_log``;
  - deterministic replay read order preserved via ``ORDER BY seq ASC``;
  - snapshot pruning constrained to retention window without changing event-log truth.

4. Determinism Verification
---------------------------

- **Replay tests executed:**

  - ``PYTHONPATH=src pytest -q tests/application/test_event_store_integration.py tests/application/test_snapshot_recovery.py``
  - ``PYTHONPATH=src pytest -q tests/persistence/test_payload_hash_determinism.py tests/application/test_recovery_determinism.py``
  - ``PYTHONPATH=src pytest -q tests/persistence -m postgres``

- **Results:** deterministic replay behavior remained preserved in the executed suite; ordering constraints remain sequence-based and independent of timestamps.
- **Edge cases observed:** in this environment, PostgreSQL-marked tests may be skipped when DB runtime is unavailable; skip behavior is explicit and deterministic.

Determinism claims must align with :doc:`../../engineering/determinism_and_replay`.

5. Performance Validation
-------------------------

- **Throughput:** no full load benchmark executed in this run.
- **p95 / p99 latency:** marked as TBD in the DB adapter envelope section.
- **Memory usage:** no domain-memory model change; DB metrics are observational side channels.
- **Snapshot cost:** save/load now measured in DB adapter latency metrics and pruning enables bounded retained snapshots per stream.
- **Inference latency (if applicable):** unchanged.
- **Optimization latency (if applicable):** unchanged.

Performance acceptance must reference :doc:`../../engineering/performance_budget`.

6. Load Testing Results
-----------------------

- **Load profile used:** not executed in this phase report.
- **Duration:** not executed.
- **Failure conditions observed:** not executed.
- **Replay validation result:** replay equivalence validated in deterministic integration subset; DB-specific load envelopes remain pending dedicated runtime load campaign.

Use protocol alignment with :doc:`../../engineering/local_load_testing_protocol`.

7. Contract Validation
----------------------

- **Invariants tested:**

  - version uniqueness conflict raises ``VersionConflictError``;
  - duplicate idempotent ingest returns ``AppendResult.ALREADY_EXISTS``;
  - snapshot pruning keeps latest N versions deterministically;
  - recovery equivalence preserved after pruning;
  - DB adapter error counters increment on forced DB error.

- **Violations found:** no unresolved contract violations in validated tests.
- **Resolution steps:** migration hardening added as additive ``0002`` (without rewriting ``0001``), and append semantics changed to explicit signaling for idempotency/conflict conditions.

8. Failure Propagation Observations
-----------------------------------

- **H failures:** unchanged.
- **V failures:** unchanged.
- **Inference failures:** unchanged.
- **Optimization failures:** unchanged.
- **Recovery behavior:** recovery still performs latest-snapshot restore + tail replay by logical version with load order determined by ``seq ASC``.

9. Architectural Trade-offs
---------------------------

- **Performance vs clarity:** explicit append result/conflict semantics increase adapter complexity but improve safety/auditability under concurrency.
- **Memory vs speed:** pruning reduces snapshot storage growth while preserving event-log replay truth.
- **Determinism safeguards:** sequence-ordered reads, explicit conflict signaling, and canonical payload hashing remain enforced.
- **Simplifications made:** batch append policy chosen as atomic fail-fast on any ``ALREADY_EXISTS`` member.

10. Known Limitations
---------------------

- **Technical debt introduced:** DB envelope thresholds (p95/p99/throughput) remain TBD pending controlled load campaign.
- **Performance ceilings:** fallback connection mode (without pool) may limit sustained append throughput.
- **Unresolved risks:** production scale requires periodic index/retention review and dedicated performance regression baselines.

11. Phase Gate Decision
-----------------------

- **Passed with warnings**

Warnings:

- Full end-to-end performance/load envelope validation for DB mode remains pending dedicated load-test execution with stable PostgreSQL runtime.

12. Next Phase Preparation
--------------------------

- **Dependencies satisfied:** hardened constraints, explicit append semantics, pruning policy, and DB adapter metrics are in place.
- **Risks for next phase:** tuning required for high-concurrency append workloads and pool sizing under sustained ingestion.
- **Refactoring required before next phase:** export DB adapter metrics through unified metrics pipeline and define concrete p95/p99/throughput SLO targets.

Required Cross-References
-------------------------

This report aligns conclusions with:

- :doc:`../../architecture/system_blueprint`
- :doc:`../../engineering/performance_budget`
- :doc:`../../engineering/implementation_roadmap`
- :doc:`../../engineering/local_load_testing_protocol`
- :doc:`../../engineering/internal_metrics_architecture`
- :doc:`../../engineering/determinism_and_replay`
