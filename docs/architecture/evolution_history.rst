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
