Ingestion and State Reconstruction Model
========================================

1. Introduction
---------------

This document defines the ingestion and state reconstruction architecture of the Data Center Digital Twin.

The Digital Twin must:

- Consume events from real infrastructure
- Reconstruct the current state of a hyperscale data center
- Preserve determinism
- Support replay
- Support synthetic simulation
- Maintain strict separation between infrastructure and domain

Ingestion does not modify domain logic.
It only translates external information into domain events.

---

2. Architectural Overview
-------------------------

The ingestion pipeline is structured as:

::

    IoT Devices / Telemetry Sources
        ↓
    Infrastructure Adapters
        ↓
    Kafka Topics
        ↓
    Ingestion Service
        ↓
    Event Normalizer
        ↓
    Digital Twin Core
        ↓
    Snapshot

The ingestion system is responsible for:

- Event transport
- Event normalization
- Ordering guarantees
- State reconstruction consistency

---

3. Event Categories
-------------------

The Digital Twin operates with normalized domain events.

Raw infrastructure events must be mapped into one of the following domain-level categories:

Network Events:
    - FlowStarted
    - FlowEnded
    - LinkUtilizationUpdate
    - LinkCapacityUpdate
    - RoutingTableUpdate

Compute Events:
    - WorkloadStarted
    - WorkloadCompleted
    - CPUUtilizationUpdate
    - MemoryUsageUpdate

Control Events:
    - SDNPolicyUpdated
    - ServerAdded
    - ServerRemoved

Events must contain:

- Deterministic timestamp
- Unique identifier
- Source identifier
- Event payload
- Version metadata

---

4. Event Normalization
----------------------

Infrastructure events are device-specific.

Adapters must translate device payloads into canonical domain events.

Normalization must ensure:

- Schema consistency
- Unit normalization
- Timestamp normalization
- ID canonicalization

Normalization must be deterministic.

No randomness allowed.

---

5. Ordering Guarantees
----------------------

Deterministic state reconstruction requires ordered event ingestion.

The ingestion system must ensure:

1. Events are processed in non-decreasing timestamp order.
2. Events from the same partition preserve FIFO ordering.
3. Replayed sequences preserve identical ordering.

If ordering is violated:

- Ingestion must fail.
- The system must not attempt correction.

---

6. State Reconstruction Model
-----------------------------

The Digital Twin does not simulate speculative state.

It reconstructs state using:

.. math::

    X_{t+1} = H(X_t, e_t)

Each incoming event modifies only affected components.

State updates must be:

- Local
- Sparse
- Deterministic
- Contract-validated

No global recomputation is allowed.

---

7. Real-Time Operation Model
-----------------------------

The ingestion loop operates continuously:

::

    while True:
        read event from Kafka
        normalize event
        validate timestamp ordering
        twin.ingest_event(event)
        snapshot = twin.get_snapshot()
        publish snapshot to observers

Inference and optimization may run at window intervals.

The Digital Twin Core must remain synchronous and deterministic.

Concurrency may exist outside the domain.

---

8. Snapshot Strategy
--------------------

Snapshots are:

- Immutable
- Derived views of state
- Consistent across subsystems

Snapshots must support:

- Real-time dashboards
- Replay comparison
- Historical persistence

Snapshot generation must not mutate state.

---

9. Replay Mode
--------------

Replay mode replaces Kafka ingestion with stored event logs.

Replay procedure:

1. Initialize fresh Digital Twin.
2. Load recorded event sequence.
3. Inject events in original order.
4. Compare final snapshot.

Replay must produce identical state.

If mismatch occurs, determinism is violated.

---

10. Synthetic Ingestion Mode
----------------------------

Synthetic mode replaces infrastructure adapters with event generators.

SyntheticAdapter responsibilities:

- Generate FlowStarted events.
- Generate workload arrivals.
- Generate congestion scenarios.
- Simulate bursts.

Synthetic mode must use the same ingestion pipeline.

This guarantees equivalence between:

- Real operation
- Simulation mode

---

11. Fault Handling
------------------

If ingestion detects:

- Out-of-order timestamps
- Invalid schema
- Contract violation

The system must:

- Reject event
- Log failure
- Halt or quarantine

Silent correction is forbidden.

---

12. Scalability Considerations
------------------------------

For hyperscale support:

- Partition events by data center zone or cluster.
- Process partitions independently.
- Avoid global locks.
- Avoid full-state scans.
- Maintain sparse updates.

Complexity per event:

.. math::

    O(|affected\_components|)

Not:

.. math::

    O(|V| + |E|)

---

13. Infrastructure Separation
-----------------------------

Infrastructure layer may:

- Read Kafka.
- Parse device payloads.
- Persist logs.
- Emit metrics.

Infrastructure layer must not:

- Modify domain state directly.
- Skip event normalization.
- Bypass validation.
- Inject unordered events.

All domain mutations occur via twin.ingest_event().

---

14. Consistency with Contracts
------------------------------

After every event:

- Flow-level contracts must hold.
- Compute-level contracts must hold.
- Temporal contracts must hold.

Validation must execute after each state transition.

---

15. Summary
-----------

The ingestion model ensures:

- Deterministic reconstruction of hyperscale state
- Compatibility with real-time operation
- Compatibility with replay
- Support for synthetic simulation
- Strict domain isolation
- Efficient sparse updates

This architecture allows the Digital Twin to operate continuously alongside a real data center.
