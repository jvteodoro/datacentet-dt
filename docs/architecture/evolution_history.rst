Architecture Evolution History
==============================

Phase 2 — Flow-Level Network Model
----------------------------------

- Introduced flow-level state with deterministic replay support.
- Focused on correctness and immutable-style state transitions.
- Limitation identified: transition-time container copies could scale with global state size.

Phase 2.1 — Structural Separation
---------------------------------

- Separated structural topology from dynamic state.
- Moved modified-entity metadata out of committed state into transition-local payloads.
- Improved locality, but dynamic flow updates still copied full containers.

Phase 2.2 — Hyperscale Structural Refactor
------------------------------------------

- Adopted logical immutability for dynamic containers in deterministic core loop.
- Implemented in-place flow updates with transition-local rollback on validation failure.
- Preserved immutable snapshot boundary for external read paths.

Trade-offs
----------

- **Physical immutability** simplifies reasoning but can increase per-event costs under churn.
- **Logical immutability** with rollback preserves determinism in single-threaded execution while reducing update overhead.

Justification
-------------

The shift from physical to logical immutability was justified by hyperscale constraints:
flow transition cost must remain proportional to affected path size, not total network size,
while replay determinism and pre-commit validation guarantees remain intact.

Phase 3 — Compute Cluster Engine
--------------------------------

- Added immutable compute topology + dynamic compute usage arrays.
- Added sparse workload lifecycle tracking with local rollback.
- Preserved :math:`O(1)` workload start/end transitions.

Phase 4 — Temporal Evolution Engine
-----------------------------------

- Introduced explicit ``Tick`` event for discrete-time progression.
- Added active-entity tracking:

  - ``active_link_indices`` for backlog drain locality
  - ``active_server_indices`` for active compute locality

- Added temporal drain/progress laws:

  - network backlog drains by capacity over ``delta_time``
  - workload remaining demand decreases by ``cpu_usage_rate * delta_time``

- Tick transition applies local in-place updates with transition-local rollback
  and modified-entity validation only.

Structural vs dynamic evolution
-------------------------------

- Structural evolution remains event-driven and mostly append-style
  (nodes/links/servers).
- Dynamic evolution now includes both causal events (flow/workload start/end)
  and temporal events (tick progression).

Trade-offs
----------

- Modeling time as explicit events increases event volume under fine-grained
  simulation.
- In return, replay determinism is preserved and temporal work remains sparse,
  bounded by active entities rather than full graph/server cardinality.

Phase 4.1 — Deterministic Ordering Canonicalization
----------------------------------------------------

- Canonicalized Tick iteration over active temporal collections.
- Replaced implicit set/dict traversal with explicit sorted traversal for:

  - ``active_link_indices``
  - ``active_workloads`` keys

- Preserved active-only locality and rollback discipline.
- Elevated determinism posture from functional replay equivalence to structural
  iteration canonicalization in temporal evolution loops.

Phase 5 — Event Store & Persistence Architecture
------------------------------------------------

- Introduced persistence ports:

  - ``EventStore`` (append/load/load_from)
  - ``SnapshotStore`` (save/load_latest)

- Refactored ``DataCenterTwin`` from internal in-memory event list to
  event-store-backed persistence with snapshot interval policy.
- Added deterministic recovery flow:

  - load latest snapshot
  - replay events after snapshot version

- Preserved deterministic transition/validation ordering and logical
  immutability boundaries.
- Established integration path for future Kafka-backed event transport and
  durable persistence adapters.


Phase 6 — Introduction of Epistemological Layer
------------------------------------------------

- Added an inference subsystem decoupled from physical transition logic.
- Introduced deterministic strategy orchestration with immutable parameter outputs.
- Added online moving-average estimation over active-entity metrics only.
- Enforced epistemic contracts (finite values, covariance checks, timestamp monotonicity).


Micro-Phase 6.1 — Epistemological Determinism Hardening
--------------------------------------------------------

- Formalized inference runtime modes: ``LIVE``, ``REPLAY``, and ``DISABLED``.
- Canonicalized epistemic timestamp source to ``snapshot.version_counter``.
- Hardened hyperscale policy: moving-average extraction uses aggregated active metrics only.
- Added ``ParameterStore`` persistence port for immutable parameter vectors.


Phase 6.2 — EKF Strategy: covariance-carrying epistemic estimator introduced
-------------------------------------------------------------------------------

- Added ``EKFStrategy`` under inference strategies with deterministic 2D EKF update.
- Introduced nonlinear observation model in log-space with aggregate-only snapshot inputs.
- Added Joseph-form covariance updates, symmetrization, and deterministic inversion jitter for PSD stability.
- Preserved strict separation from physical domain state and replay-equivalent LIVE/REPLAY execution.


Phase 7 — Optimization Architecture
-----------------------------------

- Added strategy-based optimization subsystem decoupled from domain mutation path.
- Introduced deterministic strategy registry and orchestration engine modes: ``LIVE``, ``REPLAY``, ``DISABLED``.
- Added immutable ``ActionProposal`` model and fail-fast admissibility/safety contracts.
- Added baseline O(1) optimization policy based on aggregated backlog metric.
- Enforced optimization re-entry through ``ControlActionProposed`` domain events to preserve replay determinism.


Phase 8 — Real Database Persistence Backend
-------------------------------------------

- Replaced in-memory-only persistence path with PostgreSQL-backed adapters for
  ``EventStore`` and ``SnapshotStore`` ports.
- Preserved append-only event log as authoritative source of truth.
- Added canonical JSON SHA-256 hashing for persisted event payloads and snapshot
  payload bytes to harden determinism integrity and corruption detection.
- Kept snapshot semantics as acceleration-only for recovery (load latest snapshot,
  replay tail events by logical version while preserving DB read order by ``seq``).
- Maintained domain transition and validation semantics unchanged through
  ports/adapters dependency injection.


Phase 8.1 — Persistence Hardening
---------------------------------

- Added additive hardening migration ``0002_hardening.sql`` to enforce stream-level
  invariants: unique logical version per stream and idempotent ingest token per stream.
- Hardened append semantics with explicit idempotency signaling
  (``AppendResult.ALREADY_EXISTS``) and deterministic ``VersionConflictError`` on
  logical version collisions.
- Added operational snapshot compaction policy (keep latest N per stream) without
  changing replay semantics or event-log source-of-truth posture.
- Introduced DB adapter observational metrics (append/snapshot latency and error counters)
  as side channels aligned with metrics architecture.
- Added connection-factory/pooling support with context-managed transaction boundaries
  for safer concurrent persistence operations.


Phase 9A — Kafka Streaming Ingestion Adapter + unified stack compose
---------------------------------------------------------------------

- Added infrastructure streaming adapter package under
  ``digital_twin.infrastructure.streaming`` with Kafka message schema validation,
  normalization, and single-threaded consumer loop.
- Added Kafka consumer semantics aligned to deterministic ingest protocol:

  - normalize -> H -> V -> commit -> persist -> snapshot remains enforced by
    domain ingest path;
  - duplicate ingest IDs return ``ALREADY_EXISTS`` and skip state mutation;
  - version conflicts raise deterministic divergence errors;
  - invalid payloads route to DLQ and commit offsets.

- Added project-level stack compose file ``docker-compose.stack.yml`` including
  PostgreSQL + ZooKeeper + Kafka + Kafka UI (+ pgAdmin optional).
- Added streaming test suite (unit + kafka-marked integration-contract tests)
  for schema validation, mapping, idempotency, ordering, and DLQ handling.
- Added engineering protocol doc for local Kafka stack operations and tests.


Phase 9C — Hyperscale Multi-Stream Partition Strategy
------------------------------------------------------

- Added ``MultiStreamCoordinator`` to route by ``stream_id`` into isolated
  ``DataCenterTwin`` instances (one twin per stream).
- Extended Kafka consumer adapter for multi-stream outcomes
  (``APPLIED``, ``DUPLICATE``, ``DLQ``, ``VERSION_CONFLICT``) with offset
  commit policy aligned to DB persistence and conflict-stop semantics.
- Added telemetry producer partition-key policy (Kafka key = ``stream_id``).
- Expanded streaming tests for stream isolation, per-stream ordering,
  per-stream duplicate semantics, and partition-key routing contract.
- Documented hyperscale partitioning semantics and non-goal of global ordering
  across streams.


Phase 9C.1 — Hyperscale Hardening: TTL/LRU eviction, rebalance safety, streaming metrics
------------------------------------------------------------------------------------------

- Hardened ``MultiStreamCoordinator`` with bounded-memory operations using
  monotonic-time TTL and LRU capacity eviction.
- Added stream lifecycle operations and outcomes for deterministic, operational
  twin eviction without altering event-log source-of-truth semantics.
- Added streaming metrics side-channel collector for active streams, eviction
  counters, ingestion outcomes, and coordinator latency observations.
- Added consumer rebalance safety handling to stop processing revoked
  partitions and avoid committing unprocessed offsets.
- Documented hot-stream mitigation via substream namespace split strategy for
  horizontal scaling without global ordering assumptions.

Phase 9D — Unified Observability + Metrics API
-----------------------------------------------

- Added unified observability model for counters, gauges, and histogram-style
  aggregates with deterministic JSON serialization ordering.
- Introduced provider-backed registry for domain ingestion metrics, streaming
  operational metrics, and persistence adapter metrics.
- Added lightweight read-only Metrics API endpoints for health, snapshot export,
  schema discovery, and stream-level operational aggregates.
- Formalized determinism-safe observability semantics: metrics remain
  side-channel only and never mutate domain transition/replay behavior.

Phase 9D.1 — Metrics cache and staleness contract
--------------------------------------------------

- Added TTL-based ``MetricsSnapshotCache`` with monotonic clock abstraction for
  deterministic, testable refresh policy.
- Updated metrics API serving path to use cache-backed snapshot retrieval,
  reducing repeated per-request collection overhead under burst traffic.
- Formalized staleness semantics and failure fallback: return last cached
  snapshot on refresh failure and increment observability refresh-error counter.


Phase 9D.2 — Metrics coverage expansion + cardinality policy
--------------------------------------------------------------

- Expanded observability snapshot with bounded ``topk`` and fixed-bin
  ``histograms`` blocks, preserving deterministic-safe serialization ordering.
- Added network/compute insight providers using snapshot-only reads for
  aggregate always-on metrics plus bounded Top-K and histogram exports.
- Added read-only cache-backed endpoints ``/metrics/top`` and
  ``/metrics/histograms`` with hard limit enforcement.
- Formalized observability cardinality/cost policy and deterministic ordering
  requirements for hyperscale-safe request behavior.

Phase 9E — Local Locust Load-Testing Suite for Metrics API
-----------------------------------------------------------

- Added a dedicated ``load_testing/locust`` suite with deterministic profile
  definitions for cache-hit, burst, refresh-pressure, and mixed-observability
  scenarios.
- Introduced environment-driven endpoint weights, runtime parameters, and
  header injection support for future auth simulation.
- Formalized safe refresh-pressure methodology using TTL-aligned waits rather
  than mutation endpoints.
- Added local operator documentation and acceptance-gate placeholders linking
  Locust scenarios to performance budget reporting fields.
