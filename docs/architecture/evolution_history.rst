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
