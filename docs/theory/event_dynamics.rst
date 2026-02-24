Event Dynamics
==============

1. Introduction
---------------

This document formally defines the event-driven dynamics of the Data Center Digital Twin.

The system evolves through discrete events applied to a composed state.  
The transition mechanism is implemented by the internal event bus and constitutes the operator:

.. math::

   H : (X_k, e_k) \rightarrow X_{k+1}

This document explains:

- How events are processed
- How time progression is handled
- How causal chains are formed
- Why the system is deterministic
- How subsystem composition occurs

---

2. Events as Atomic State Transitions
--------------------------------------

An event represents an atomic, immutable occurrence in time.

Each event:

- Has a unique identity
- Has a timestamp
- Is immutable
- Can trigger state changes

Events are not state.
They are inputs to the transition operator.

---

3. Formal Definition of the Transition Operator
-----------------------------------------------

The Digital Twin transition operator is implemented indirectly by the internal event bus.

The evolution process is:

1. An event :math:`e_k` is published.
2. The event is inserted into an internal queue.
3. The queue is processed sequentially.
4. Subscribers receive the event.
5. Subscribers may produce derived events.
6. Derived events are appended to the queue.
7. Processing continues until the queue is empty.

Formally:

.. math::

   X_{k+1} = H(X_k, e_k) =
   H_n(...H_2(H_1(X_k, e_k))...)

Where each :math:`H_i` corresponds to a subsystem reaction.

---

4. Deterministic Processing Model
----------------------------------

The system guarantees determinism through:

- Ordered event queue
- No concurrency
- No asynchronous processing
- Pure domain logic

Given:

- Same initial state
- Same ordered event sequence

The system must produce identical final states.

This property is required for:

- Replay
- Auditing
- Scientific reproducibility

---

5. Event Queue Semantics
------------------------

The internal event bus maintains:

- A FIFO queue
- A mapping of event types to subscribers

Processing rules:

- Events are dequeued one at a time.
- All registered subscribers for the event type are invoked.
- If a subscriber publishes a new event, it is appended to the queue.
- The publish() method only returns after the queue is empty.

This ensures closure of causal chains.

---

6. Hybrid Time Evolution
------------------------

The system is hybrid:

- Discrete in event application
- Continuous in physical evolution between events

When an event with timestamp :math:`t_k` is applied:

.. math::

   \Delta t = t_k - t_{k-1}

Subsystems must:

- Advance internal physical state by :math:`\Delta t`
- Then apply the discrete effect of the event

No time progression is allowed without explicit timestamp advancement.

---

7. Causal Chains
----------------

Events can generate new events.

Example:

.. code-block:: text

   WorkloadSubmitted
       ↓
   WorkloadDelivered
       ↓
   TaskStarted
       ↓
   TaskCompleted

This forms a causal chain.

The system guarantees:

- Causal closure
- Ordered processing
- No partial state exposure

---

8. Isolation of Infrastructure
------------------------------

The event bus is part of the domain.

It does not:

- Use Kafka
- Use threads
- Use async
- Use external frameworks

Infrastructure delivers external events to the system,
but does not participate in internal dynamics.

---

9. Safety Guarantees
--------------------

The event dynamics guarantee:

- No lost events
- No duplicated deliveries
- No recursion-based stack overflow
- No out-of-order processing

Violations must raise explicit errors.

---

10. Relationship to Validation Operator
----------------------------------------

The transition operator H modifies state.

After each complete causal chain:

.. math::

   V(X_{k+1}) \rightarrow \{\text{valid}, \text{error}\}

Validation is separate from evolution.

Evolution does not silently correct errors.
Validation enforces invariants.

---

11. Why Concurrency is Excluded (MVP)
--------------------------------------

Concurrency introduces:

- Non-determinism
- Race conditions
- Order ambiguity

The MVP intentionally excludes concurrency to guarantee:

- Determinism
- Reproducibility
- Mathematical clarity

Parallel execution may be introduced in future versions
with formal concurrency semantics.

---

12. Extensibility
-----------------

Future extensions must:

1. Define event types
2. Define state variables
3. Define evolution laws
4. Register subscribers
5. Update validation rules

No extension may bypass the event bus.

All state evolution must pass through H.

---

13. Summary
-----------

The Digital Twin evolves according to:

.. math::

   X_{k+1} = H(X_k, e_k)

Where H is:

- Deterministic
- Ordered
- Composed
- Closed under causal generation

This defines the operational semantics of the Digital Twin.