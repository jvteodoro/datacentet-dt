Contracts and Domain Invariants
===============================

1. Introduction
---------------

This document defines the normative contracts of the Data Center Digital Twin.

Contracts are formal conditions that must hold for the system state to be considered valid.

They are not mere assertions.
They are expressions of physical, logical, and causal laws.

The validation operator V enforces these contracts:

.. math::

   V : X_k \rightarrow \{\text{valid}, \text{error}\}

A contract violation indicates that the system has entered a physically impossible or logically inconsistent state.

---

2. Taxonomy of Contracts
------------------------

Contracts are divided into four categories:

1. Conservation Laws
2. Physical Limit Constraints
3. Temporal Consistency Rules
4. Causal Consistency Rules

Each category protects a different dimension of system integrity.

---

3. Conservation Laws
--------------------

Conservation laws express that quantities cannot be created or destroyed.

They ensure numerical integrity of the model.

3.1 Network Flow Conservation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Formal statement:

.. math::

   \text{total_arrived} =
   \text{total_served} +
   \text{total_dropped} +
   \text{current_depth}

Meaning:

- Every unit that enters the queue must either:
  - Be served,
  - Be dropped,
  - Or remain in the backlog.

Why this is necessary:

Without this law, the system could silently:

- Lose traffic
- Create traffic
- Drift numerically over time

Violation implies mathematical corruption.

---

3.2 Computational Work Conservation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Formal statement:

.. math::

   \text{required_cycles} =
   \text{processed_cycles} +
   \text{remaining_cycles}

Meaning:

- Computational work cannot disappear.
- CPU cannot produce negative or extra cycles.

Why this is necessary:

Without it, the model could:

- Complete tasks prematurely
- Accumulate phantom work
- Drift under floating point errors

Violation implies invalid simulation of CPU physics.

---

4. Physical Limit Constraints
-----------------------------

These constraints enforce hardware boundaries.

4.1 Queue Capacity Limit
~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   \text{current_depth} \le \text{capacity}

Why:

Buffers are finite.
Exceeding capacity violates physical realism.

If violated:

- Either arrival handling is incorrect
- Or service computation is flawed

---

4.2 Memory Capacity Limit
~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   \text{memory_allocated} \le \text{memory_capacity}

Why:

A server cannot allocate more memory than available.

Violation implies invalid resource modeling.

---

4.3 CPU Throughput Bound
~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   \text{processed} \le \text{cpu_capacity} \cdot \Delta t

Why:

CPU cannot process more work than physically allowed.

Violation implies invalid time evolution logic.

---

5. Temporal Consistency Rules
-----------------------------

The system is hybrid and time-indexed.

5.1 Non-Decreasing Timestamps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   t_{k+1} \ge t_k

Why:

Backward time progression is physically impossible.

Violation implies:

- Out-of-order event ingestion
- Event bus corruption
- Replay corruption

---

5.2 Positive Time Delta
~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   \Delta t \ge 0

Negative time deltas are forbidden.

---

6. Causal Consistency Rules
---------------------------

Causality protects inter-subsystem coherence.

6.1 Delivery Before Execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If:

.. math::

   \text{TaskStarted}(t_s)

Then:

.. math::

   \exists \text{WorkloadDelivered}(t_d)

Such that:

.. math::

   t_s \ge t_d

Why:

A workload must physically arrive before execution begins.

Violation implies logical impossibility.

---

7. Deterministic Consistency
----------------------------

7.1 Replay Equivalence
~~~~~~~~~~~~~~~~~~~~~~

Given identical:

- Initial state
- Event sequence

The final state must be identical.

Formally:

.. math::

   X_k^{(run1)} = X_k^{(run2)}

Why:

Scientific reproducibility requires determinism.

Violation implies:

- Hidden state mutation
- Concurrency side effects
- Non-deterministic ordering

---

8. Structural Invariants
------------------------

Structural invariants protect system composition.

Examples:

- Snapshots must be immutable.
- Validation must not mutate state.
- EventBus must process FIFO.
- No event may bypass the EventBus.

These protect architectural integrity.

---

9. Interaction Between Contracts
---------------------------------

Contracts must be mutually consistent.

Example:

Conservation laws assume:
- Non-negative quantities
- Capacity constraints respected

Temporal consistency underpins:
- CPU throughput bound
- Service rate calculations

Causal consistency depends on:
- Correct event ordering

Therefore:

Breaking one contract may cascade into others.

Validation must report first violation detected.

---

10. Failure Philosophy
----------------------

The system must fail loudly and explicitly.

If a contract fails:

- Raise exception.
- Stop evolution.
- Do not auto-correct.

Silent tolerance corrupts scientific validity.

---

11. Floating Point Considerations
---------------------------------

Because the system uses real numbers:

- Comparisons must allow small tolerances (epsilon).
- Conservation checks must account for numerical precision.

Epsilon must be defined explicitly.

---

12. Extension Rule
------------------

When introducing a new feature:

1. Define its conserved quantities (if any).
2. Define its physical limits.
3. Define its temporal behavior.
4. Define causal constraints.
5. Extend the validation operator.

No feature may exist without contracts.

---

13. Summary
-----------

Contracts define the normative boundaries of the Digital Twin.

They guarantee:

- Physical realism
- Logical coherence
- Temporal consistency
- Causal validity
- Deterministic replay

Without contracts:

The system is a simulator.

With contracts:

The system is a scientifically grounded Digital Twin.