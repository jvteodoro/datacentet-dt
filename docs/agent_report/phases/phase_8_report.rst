Phase 8 Report — Real Database Persistence Backend
==================================================

1. Phase Overview
-----------------

- **Phase number:** 8
- **Date:** 2026-02-25
- **Commit reference (if available):** ``4145e02``
- **Related roadmap section:** :doc:`../../engineering/implementation_roadmap`

2. Architectural Scope
----------------------

- **Components introduced:** ``digital_twin.infrastructure.db`` package with PostgreSQL connection/migration helpers, ``EventStorePG``, ``SnapshotStorePG``, and SQL migration ``0001_init.sql``.
- **Documents modified:** ``docs/architecture/evolution_history.rst``, ``docs/engineering/real_db_protocol.rst``, and ``docs/engineering/index.rst``.
- **Contracts affected:** persistence boundary contracts for append-only event log semantics, replay ordering by DB sequence, and deterministic canonical payload hashing.
- **Data structures introduced:** relational tables ``event_log`` and ``snapshot_store`` with stream/version/hash metadata.

Reference architecture baseline: :doc:`../../architecture/system_blueprint`.

3. Formal Model Impact
----------------------

- **Impact on** :math:`(X, E, H, V, \mathcal{I}, \mathcal{O})`: no change in domain transition operator :math:`H`, validator :math:`V`, inference :math:`\mathcal{I}`, or optimization :math:`\mathcal{O}`; persistence substrate for event space :math:`E` was upgraded from in-memory to durable PostgreSQL storage.
- **State extensions (if any):** no extension to in-memory domain state ``X``.
- **Invariant extensions (if any):** persistence integrity invariants added via canonical SHA-256 hashing for event payloads and snapshot payload bytes.

Persistence/recovery law preserved:

.. math::

   X_t = \mathrm{replay}(X_0, e_1, \ldots, e_t),\quad
   X_t = \mathrm{replay}(X_s, e_{s+1}, \ldots, e_t)

where :math:`X_s` is acceleration snapshot only, and event truth remains authoritative.

4. Determinism Verification
---------------------------

- **Replay tests executed:**

  - ``PYTHONPATH=src pytest -q tests/application/test_event_store_integration.py tests/application/test_snapshot_recovery.py tests/application/test_recovery_determinism.py tests/persistence/test_payload_hash_determinism.py``
  - ``PYTHONPATH=src pytest -q tests/persistence -m postgres``

- **Results:** deterministic replay equivalence remained preserved in the validated subset; canonical hash determinism test passed; PostgreSQL-marked integration tests were correctly isolated by marker and skipped when runtime DB was unavailable.
- **Edge cases observed:** environment without Docker/PostgreSQL cannot execute DB integration path; test suite behavior was explicitly configured to skip with clear fixture messaging.

Determinism claims must align with :doc:`../../engineering/determinism_and_replay`.

5. Performance Validation
-------------------------

- **Throughput:** not benchmarked with load profile in this environment.
- **p95 / p99 latency:** not benchmarked in this environment.
- **Memory usage:** domain-memory semantics unchanged; persistence moved to DB adapter boundary.
- **Snapshot cost:** snapshot writes now include canonical serialization + SHA-256, then DB insert/update by ``(stream_id, version_counter)``.
- **Inference latency (if applicable):** unchanged.
- **Optimization latency (if applicable):** unchanged.

Performance acceptance must reference :doc:`../../engineering/performance_budget`.

6. Load Testing Results
-----------------------

- **Load profile used:** not executed in this phase report.
- **Duration:** not executed.
- **Failure conditions observed:** not executed.
- **Replay validation result:** replay recovery equivalence retained in deterministic unit/integration subset; DB-specific scenarios require local Postgres runtime.

Use protocol alignment with :doc:`../../engineering/local_load_testing_protocol`.

7. Contract Validation
----------------------

- **Invariants tested:**

  - append-only ``event_log`` writes with single-row append operation;
  - replay ordering by ``seq ASC`` (never by timestamps);
  - ``load_from`` filtering by ``version_counter > snapshot.version_counter``;
  - canonical payload hashing stability independent of key insertion order;
  - latest snapshot retrieval by highest ``version_counter``.

- **Violations found:** no determinism or contract violation found in executed tests.
- **Resolution steps:** pytest marker ``postgres`` was registered and DB-dependent fixtures were isolated to avoid false negatives in environments without Docker/PostgreSQL.

8. Failure Propagation Observations
-----------------------------------

- **H failures:** unchanged domain behavior.
- **V failures:** unchanged validation behavior.
- **Inference failures:** unchanged.
- **Optimization failures:** unchanged.
- **Recovery behavior:** when snapshot exists, recovery restores snapshot and replays event tail; when absent, replays full event stream. Ordering remains sequence-based.

9. Architectural Trade-offs
---------------------------

- **Performance vs clarity:** SQL persistence adds complexity versus in-memory stores, but gives durable reproducibility and auditable event history.
- **Memory vs speed:** snapshot acceleration retained to reduce replay cost, while event log remains source of truth.
- **Determinism safeguards:** canonical JSON hashing + ordered replay by monotonic DB ``seq`` + stream scoping.
- **Simplifications made:** migration mechanism is SQL-file driven without external migration framework to keep adapter layer minimal.

10. Known Limitations
---------------------

- **Technical debt introduced:** no dedicated observability export yet for DB adapter latency/throughput histograms.
- **Performance ceilings:** no local load-test percentile dataset captured for DB mode in this run.
- **Unresolved risks:** operational deployment must enforce strict migration discipline and index health for high-volume append/replay workloads.

11. Phase Gate Decision
-----------------------

- **Passed with warnings**

Warnings:

- PostgreSQL integration tests require local runtime (Docker or equivalent Postgres service) and could not be executed end-to-end in this environment.

12. Next Phase Preparation
--------------------------

- **Dependencies satisfied:** durable persistence adapters, migration baseline, replay-ordering safeguards, and deterministic hash integrity checks are in place.
- **Risks for next phase:** performance tuning may be required for large streams (index/selectivity, connection pooling, batching strategy).
- **Refactoring required before next phase:** add persistence metrics export aligned with internal metrics architecture and performance budget reporting.

Required Cross-References
-------------------------

This report aligns conclusions with:

- :doc:`../../architecture/system_blueprint`
- :doc:`../../engineering/performance_budget`
- :doc:`../../engineering/implementation_roadmap`
- :doc:`../../engineering/local_load_testing_protocol`
- :doc:`../../engineering/internal_metrics_architecture`
- :doc:`../../engineering/determinism_and_replay`
