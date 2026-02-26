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
