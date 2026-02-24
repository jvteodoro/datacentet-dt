System Architecture Blueprint
=============================

1. Purpose
----------

This document consolidates the complete architecture of the Data Center Digital Twin.

It integrates:

- Flow-level physical modeling
- Contracts and invariants
- Event ingestion
- Inference layer
- Optimization layer
- Persistence model
- Deterministic replay
- Hyperscale scalability principles

The system is formally defined as:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

Where:

- X = global state
- E = event space
- H = deterministic transition operator
- V = validation operator
- 𝓘 = inference operator
- 𝓞 = optimization operator

---

2. Architectural Layers
-----------------------

The architecture is organized into six major layers:

::

    Infrastructure Layer
    Event Streaming Layer
    Ingestion Layer
    Digital Twin Core
    Inference Layer
    Optimization Layer

Each layer has strict responsibility boundaries.

---

3. Infrastructure Layer
-----------------------

Responsibilities:

- Communicate with IoT devices
- Collect telemetry
- Publish events to Kafka
- Persist validated events and validated snapshots
- Provide synthetic event generators

Must NOT:

- Modify domain state
- Skip event normalization
- Bypass validation
- Inject unordered events

Infrastructure is replaceable.

---

4. Event Streaming Layer
------------------------

Kafka (or equivalent) serves as:

- Transport backbone
- Partition manager
- Ordering mechanism
- Durability layer

Event ordering guarantees:

- FIFO within partition
- Non-decreasing timestamps
- Deterministic replay capability

---

5. Ingestion Layer
------------------

Responsibilities:

- Consume events from streaming layer
- Normalize device-specific payloads
- Validate ordering constraints
- Convert raw telemetry into domain events
- Inject normalized events into Digital Twin Core

State reconstruction follows:

.. math::

   X_{t+1} = H(X_t, e_t)

No speculative state is allowed.

---

6. Digital Twin Core (Domain Layer)
------------------------------------

The domain layer implements:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

It contains:

- Flow-level network graph
- Compute cluster model
- Workload profile model
- Transition operator H
- Validation operator V

The domain must be:

- Deterministic
- Pure
- Infrastructure-independent
- Replayable
- Contract-validated

---

6.1 Global State Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   X_t =
   \begin{bmatrix}
   G_{net,t} \\
   G_{comp,t} \\
   \Phi_t
   \end{bmatrix}

Where:

- G_net = flow-level network graph
- G_comp = compute cluster state
- Φ = workload statistical profile

---

6.2 Flow-Level Modeling
~~~~~~~~~~~~~~~~~~~~~~~

Network:

.. math::

   G_{net} = (V, E)

Compute:

.. math::

   G_{comp} = (S, R)

State evolution is sparse and event-driven.

Complexity per event:

.. math::

   O(|affected\_components|)

Not:

.. math::

   O(|V| + |E|)

---

6.3 Contracts and Invariants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The validation operator V enforces:

- Link capacity constraints
- CPU capacity constraints
- Memory bounds
- Flow conservation
- Workload conservation
- Temporal consistency
- Routing validity
- Deterministic replay

Violations halt execution.

---

7. Inference Layer
------------------

The inference layer estimates parameter vector:

.. math::

   \theta_{t+1} = \mathcal{I}(X_t, Y_t)

Responsibilities:

- Parameter calibration
- Workload profile updates
- Drift correction
- Noise handling

Must:

- Use Strategy Pattern
- Be deterministic
- Not mutate domain state

Supported strategies:

- Least squares
- Online gradient
- Kalman filter
- Bayesian inference

---

8. Optimization Layer
---------------------

Optimization computes control actions:

.. math::

   u_t = \mathcal{O}(X_t, \theta_t)

Responsibilities:

- Congestion minimization
- Energy-aware scheduling
- SLA enforcement
- Load balancing
- Capacity planning

Must:

- Use Strategy Pattern
- Be deterministic
- Return control events
- Never mutate state directly

All actions must re-enter system via ingestion.

---

9. Persistence and Historical Memory
-------------------------------------

Persistence consists of:

Event Store:
    - Append-only event log
    - Source of truth

Snapshot Store:
    - Sparse state checkpoints
    - Restart acceleration

Metric Store:
    - Aggregated window metrics

Replay procedure:

1. Load snapshot
2. Replay subsequent events
3. Validate final state

Replay must reproduce identical X_t.

---

10. Synthetic Simulation Mode
-----------------------------

Synthetic adapters generate events instead of reading from IoT.

Uses same ingestion pipeline.

Ensures equivalence between:

- Real-world mode
- Simulation mode
- Offline experiments

---

11. Real-Time Operation Model
-----------------------------

Operational loop:

::

    read event
    normalize
    H
    V
    if valid: persist
    if valid: snapshot update
    if valid: inference window update
    inference (windowed)
    optimization (windowed)
    emit control actions

Domain execution remains synchronous and deterministic.

Invalid transitions must not be persisted and must not trigger snapshot or inference-window updates.

Parallelism may exist outside domain.

---

12. Determinism and Scientific Integrity
----------------------------------------

Given identical:

- Initial state :math:`X_0`
- Ordered event sequence :math:`(e_1, \dots, e_n)`
- Initial parameter vector :math:`\theta_0`
- Identical inference and optimization seeds (if applicable)

The system must produce identical:

- State :math:`X_n`
- Validation outcomes
- Parameter vector :math:`\theta_n`
- Control actions :math:`u_n`

Determinism is non-negotiable.

---

13. Scalability Principles
--------------------------

To support hyperscale:

- Sparse data structures
- Event-driven local updates
- Partitioned ingestion
- Window-based inference
- Heuristic optimization in online mode
- Delta-based snapshotting

Global scans are forbidden.

---

14. Extension Philosophy
------------------------

Any new feature must:

1. Define state variables
2. Define transition laws
3. Define invariants
4. Extend validation operator
5. Preserve determinism
6. Respect layer boundaries

Infrastructure-first design is forbidden.

---

15. System Summary
------------------

The Digital Twin architecture provides:

- Flow-level hyperscale modeling
- Deterministic state reconstruction
- Strict invariant enforcement
- Modular inference
- Modular optimization
- Real-time ingestion
- Synthetic experimentation
- Historical reproducibility

The system is not a dashboard.
It is a mathematically grounded, scalable, adaptive Digital Twin platform.

16. Architectural Evolution: Physical vs Logical Immutability
--------------------------------------------------------------

Initial phases adopted physical immutability (new container instances per state transition)
to maximize auditability and reduce hidden mutation risk.

At hyperscale flow churn, physical immutability on dynamic containers became insufficient
because full-container copy paths increase event cost with global state size.

Phase 2.2 adopts controlled logical immutability in the deterministic single-threaded core:

- Internal state containers for dynamic fields may be mutable.
- Validation remains mandatory before commit side effects.
- On validation failure, transition-local rollback restores prior values.
- External immutability boundary is preserved by immutable snapshots.

Safety rationale:

- Domain execution is sequential (no concurrent writers in core loop).
- Replay ordering is fixed and deterministic.
- Rollback scope is restricted to modified entities.
- Snapshot export remains immutable and non-aliasing.

This evolution preserves correctness guarantees while reducing flow-event transition cost
toward strict locality over affected path elements.

17. Compute Engine — Hyperscale Logical Model
---------------------------------------------

Phase 3 introduces a compute engine that follows the same deterministic,
logical-immutability discipline established for the flow engine.

Structural vs dynamic compute separation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compute structure is immutable after construction and represented as:

- ``ComputeTopology.server_index``
- ``ComputeTopology.reverse_server_index``
- ``ComputeTopology.cpu_capacity``
- ``ComputeTopology.memory_capacity``

Dynamic compute state remains mutable only inside the deterministic core loop:

- ``cpu_usage`` (per-server current CPU usage)
- ``memory_usage`` (per-server current memory usage)
- ``active_workloads`` (workload lifecycle map)

This preserves the snapshot immutability boundary while enabling strictly local
updates in event transitions.

Local rollback discipline
~~~~~~~~~~~~~~~~~~~~~~~~~

For workload transitions, :math:`H` records pre-update usage values for the
single target server, applies in-place mutation, and validates only modified
server indices.

On validation failure, rollback restores:

- original server cpu/memory usage values
- workload map insertion/removal side effects
- version and event counters

No speculative global correction is allowed.

Complexity guarantees
~~~~~~~~~~~~~~~~~~~~~

Compute-event complexity is constrained to local entity scope:

- ``WorkloadStarted``: :math:`O(1)`
- ``WorkloadEnded``: :math:`O(1)`
- server validation: modified server only

Network-event guarantees remain unchanged:

- flow transition work: :math:`O(path\_length)`
- no global scans over links, flows, servers, or workloads in event paths

This keeps the hyperscale contract aligned with sparse, event-driven evolution.

18. Temporal Evolution Engine — Discrete Tick Model
---------------------------------------------------

Phase 4 extends the deterministic event space with a discrete temporal event:

::

   Tick(delta_time: float)

Tick as event
~~~~~~~~~~~~~

Time progression is modeled as an explicit event, not by wall-clock reads.
This preserves deterministic replay because temporal evolution is fully encoded
in the ordered event log.

Temporal network evolution
~~~~~~~~~~~~~~~~~~~~~~~~~~

Tick drains only active links tracked in ``active_link_indices``.
For each active link ``i``:

.. math::

   drained_i = \min(capacity_i \cdot \Delta t, backlog_i)

.. math::

   backlog_i \leftarrow backlog_i - drained_i

If backlog reaches zero, ``i`` is removed from ``active_link_indices``.
No scan over all links is permitted.

Temporal compute evolution
~~~~~~~~~~~~~~~~~~~~~~~~~~

Tick progresses only currently active workloads.
For workload ``w``:

.. math::

   remaining\_size_w \leftarrow remaining\_size_w - cpu\_usage\_rate_w \cdot \Delta t

When ``remaining_size`` reaches zero, workload ``w`` is removed, server usage is
released, and the server is removed from ``active_server_indices`` if no workloads
remain on that server.

Determinism and rollback implications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tick follows the same transition discipline as all domain events:

1. Record modified indices and original values.
2. Apply local in-place mutation.
3. Validate only modified entities.
4. Roll back on validation failure.
5. Commit version/event counters on success.

No threads, no hidden clocks, and no unordered side effects are introduced.

Complexity guarantees
~~~~~~~~~~~~~~~~~~~~~

Tick complexity is strictly:

.. math::

   O(|active\_links| + |active\_workloads|)

Flow events remain :math:`O(path\_length)` and workload start/end remain
:math:`O(1)`.

Active-entity tracking prevents full topology or server scans while preserving
immutable snapshot export semantics.

19. Deterministic Iteration Canonicalization (Phase 4.1)
---------------------------------------------------------

Phase 4.1 hardens Tick execution by canonicalizing iteration order over active
collections.

Why canonicalization is required
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``active_link_indices`` is a set and ``active_workloads`` is a dict-backed map.
Direct iteration over these structures is not guaranteed by the model contract
as a canonical scientific ordering primitive.

To remove implicit order dependence, Tick now applies explicit sorted traversal
over active subsets only.

Canonical Tick traversal rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Link drain loop iterates ``sorted(active_link_indices)``.
- Workload progress loop iterates ``sorted(active_workloads)`` and dereferences
  each workload id from the workload map.

This preserves sparse locality while making iteration structure explicit and
stable for replay and audit.

Complexity trade-off
~~~~~~~~~~~~~~~~~~~~

Tick complexity shifts from:

.. math::

   O(|active\_links| + |active\_workloads|)

to:

.. math::

   O(|active\_links| \log |active\_links| + |active\_workloads| \log |active\_workloads|)

No global topology scan is introduced; sorting is restricted to active
collections only.

Scientific reproducibility rationale
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Explicit canonical ordering upgrades determinism from functional behavior to
structural execution reproducibility for temporal loops, reinforcing
cross-environment replay integrity.

13. Event Sourcing & Persistence Model (Phase 5)
-------------------------------------------------

Phase 5 formalizes persistence as explicit ports with deterministic in-memory
adapters.

Canonical source of truth
~~~~~~~~~~~~~~~~~~~~~~~~~

- The append-only Event Store is the canonical system history.
- Domain state is reconstructed exclusively from persisted events (optionally
  accelerated by snapshots).
- Infrastructure persistence remains replaceable as long as ordering and
  deterministic replay semantics are preserved.

Snapshot acceleration model
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recovery uses the deterministic sequence:

::

   snapshot = SnapshotStore.load_latest()
   if snapshot:
       X = snapshot_state
       replay(EventStore.load_from(snapshot.version_counter))
   else:
       X = initial_state
       replay(EventStore.load_all())

Snapshots are immutable projections, not transition inputs; transition logic and
validation semantics remain unchanged.

Deterministic recovery process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Replay order is insertion order from the Event Store.
- Tick/event canonical ordering inside transitions is unchanged.
- Recover cycles are idempotent with respect to final state for identical event
  histories.

Domain vs infrastructure separation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Domain transition/validation code remains persistence-agnostic.
- Application ports define persistence contracts.
- Infrastructure adapters implement those ports without changing domain rules.
