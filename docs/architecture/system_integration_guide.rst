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

Given identical initial state :math:`X_0` and identical ordered event sequence :math:`(e_1, \dots, e_n)`, repeated executions must produce an identical terminal state and identical validation outcomes.

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
- Snapshots are acceleration artifacts for recovery and analytics windows.
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
2. Event is ordered, validated, and injected into domain.
3. :math:`H` computes :math:`X_{t+1}` and :math:`V` validates constraints.
4. Event and metadata are persisted to event log.
5. Windowed views update inference inputs.
6. :math:`\mathcal{I}` updates parameters.
7. :math:`\mathcal{O}` computes admissible actions.
8. Action event re-enters ingestion as a regular event.

Replay walkthrough
------------------

1. Load initial state or latest valid snapshot.
2. Read ordered event suffix from event log.
3. Reapply each event through the same ingestion/domain path.
4. Recompute final state and validation results.
5. Compare expected and replayed outcomes; mismatch is determinism failure.

Load-testing workflow walkthrough
---------------------------------

1. Define workload profile and acceptance gates.
2. Execute generators against ingestion endpoints/streams.
3. Capture throughput, p95/p99 latency, error rate, and invariant violations.
4. Run replay verification on produced logs.
5. Promote phase only if gates and replay checks pass.

Inference window walkthrough
----------------------------

1. Build rolling window :math:`W_t = [t-\Delta T, t]` from persisted events/snapshots.
2. Compute aggregate features and model inputs.
3. Run :math:`\mathcal{I}(X_t, Y_t)` to update :math:`\theta_{t+1}`.
4. Publish outputs for optimization without mutating domain state.

Optimization loop walkthrough
-----------------------------

1. Consume :math:`(X_t, \theta_t)` plus constraints.
2. Compute candidate actions and evaluate admissibility.
3. Emit optimization event(s) back into ingestion.
4. Apply via :math:`H` and validate with :math:`V`.
5. Observe outcomes and iterate on next cycle.
