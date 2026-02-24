System Integration Guide
========================

Purpose
-------

This guide explains how the complete deterministic architecture operates end-to-end for new engineers, researchers, and reviewers.

The canonical model used across the project is:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

Where domain evolution remains:

.. math::

   X_{t+1} = H(X_t, e_t),\; V(X_{t+1}) \rightarrow \{\text{valid}, \text{error}\}

Determinism definition (canonical)
----------------------------------

Given identical initial state :math:`X_0`, identical ordered event sequence :math:`(e_1, \dots, e_n)`, identical initial parameter vector :math:`\theta_0`, and identical inference/optimization seeds (when stochastic procedures are configured), repeated executions must produce identical terminal state :math:`X_n`, identical validation outcomes, identical terminal parameter vector :math:`\theta_n`, and identical control actions :math:`u_n`.

Integration map
---------------

::

    [Infrastructure + Stream]
              |
              v
         [Ingestion]
              |
              v
     [Domain Core: X,E,H,V] <----> [Persistence]
              |
              v
         [Inference 𝓘]
              |
              v
        [Optimization 𝓞]
              |
              v
   [Control/Recommendation Events]
              |
              +-----------> back to Ingestion

How ingestion connects to domain
--------------------------------

- Ingestion receives raw telemetry and control events from streaming infrastructure.
- It normalizes payloads into canonical domain events in :math:`E`.
- It enforces ordering and schema validation before calling :math:`H`.
- The domain applies transitions and :math:`V` validates invariants.

Per-event validation and persistence order
------------------------------------------

Per event, the execution order is fixed and must not be reordered:

::

    normalize -> H -> V -> persist -> snapshot update -> inference window update

Persistence is permitted only when :math:`V(X_{t+1}) = \text{valid}`.

If :math:`V(X_{t+1}) = \text{error}`, the event is rejected and the system must not persist the event, must not update snapshots, and must not update inference windows.

How domain connects to inference
--------------------------------

- Inference consumes read-only snapshots or windowed projections derived from :math:`X_t`.
- Inference never mutates :math:`X` directly and never bypasses :math:`H`.

How inference connects to optimization
--------------------------------------

- Inference outputs parameter estimates :math:`\theta_t` and uncertainty summaries.
- Optimization consumes :math:`(X_t, \theta_t)` to compute admissible actions.

How optimization re-enters ingestion
------------------------------------

- Optimization emits control/recommendation events.
- These events are treated as first-class members of :math:`E` and re-enter through ingestion.
- This preserves replayability because all state changes still happen through :math:`H`.

How persistence interacts with domain
-------------------------------------

- Event log is the source of truth.
- Snapshots are acceleration artifacts for recovery and analytics windows and contain only validated states.
- Recovery is snapshot load + replay of post-snapshot events + validation.

How load testing interacts with ingestion
-----------------------------------------

- Load generators target ingestion interfaces and stream boundaries.
- Gates are evaluated on ingestion throughput, p95/p99 latency, replay integrity, and contract violations.
- Load testing never introduces bypass paths around :math:`H` or :math:`V`.

How metrics attach without breaking determinism
------------------------------------------------

- Metrics are observational side channels outside domain mutation.
- Counters and latency measurements are collected at ingestion boundaries and asynchronous exporters.
- Metrics must not alter event ordering, state contents, or validation outcomes.

Full system lifecycle walkthrough
---------------------------------

1. Telemetry event arrives and is normalized in ingestion.
2. Event is ordered and applied through :math:`H` to produce :math:`X_{t+1}`.
3. :math:`V(X_{t+1})` is executed.
4. Only if valid, event and metadata are persisted to event log.
5. Only if valid, snapshot is updated from validated state.
6. Only if valid, windowed read models update inference inputs.
7. :math:`\mathcal{I}` updates parameters deterministically.
8. :math:`\mathcal{O}` computes admissible actions deterministically.
9. Action event re-enters ingestion as a regular event in :math:`E`.

Replay walkthrough
------------------

1. Load initial state or latest valid snapshot.
2. Read ordered event suffix from event log.
3. Reapply each event through ingestion :math:`\rightarrow H \rightarrow V`.
4. Execute inference updates deterministically.
5. Execute optimization deterministically and reproduce emitted control events.
6. Compare expected and replayed state, validation outcomes, :math:`\theta`, and control outputs; mismatch is determinism failure.

Limited replay mode may exclude inference/optimization; this must be declared explicitly and results are valid only for domain-state replay guarantees.

Load-testing workflow walkthrough
---------------------------------

1. Define workload profile and acceptance gates.
2. Execute generators against ingestion endpoints/streams.
3. Capture throughput, p95/p99 latency, error rate, and invariant violations.
4. Run replay verification on produced logs.
5. Promote phase only if gates and replay checks pass.

Inference window walkthrough
----------------------------

1. Build rolling window :math:`W_t = [t-\Delta T, t]` from persisted event log and/or validated snapshots.
2. Construct window in read-only mode; do not reorder events.
3. Compute aggregate features and model inputs without mutating domain state.
4. Run :math:`\mathcal{I}(X_t, Y_t)` to update :math:`\theta_{t+1}`.
5. Publish outputs for optimization without mutating domain state.

Optimization loop walkthrough
-----------------------------

1. Consume :math:`(X_t, \theta_t)` plus constraints.
2. Compute candidate actions and evaluate admissibility.
3. Emit optimization event(s) back into ingestion.
4. Apply via :math:`H` and validate with :math:`V`.
5. Observe outcomes and iterate on next cycle.


Failure Propagation Model
-------------------------

If :math:`H` fails:

- Event is rejected.
- State remains unchanged.
- Event is not persisted.

If :math:`V` fails:

- Event is rejected.
- State reverts to previous :math:`X_t`.
- Event is not persisted.
- Snapshot and inference window are not updated.

If inference fails:

- :math:`\theta` remains unchanged.
- Domain state remains unchanged.
- Failure is logged.

If optimization fails:

- No control events are emitted.
- Domain state remains unchanged.

Metrics and load-testing failures must:

- Not alter domain state.
- Not break determinism.
