Hexagonal Design (Ports & Adapters)
====================================

1. Introduction
---------------

The Data Center Digital Twin follows the Hexagonal Architecture pattern,
also known as Ports & Adapters.

This architectural decision is foundational.
It guarantees:

- Isolation of domain logic
- Deterministic behavior
- Testability
- Infrastructure independence
- Scientific integrity

The domain must remain pure.

---

2. Core Principle
-----------------

The system is divided into:

- Domain (pure logic)
- Application (orchestration)
- Infrastructure (external systems)

Only the domain defines the system's behavior.

Infrastructure may change.
The domain must not.

---

3. Architectural Layers
-----------------------

3.1 Domain Layer
~~~~~~~~~~~~~~~~

Contains:

- State models
- Transition laws
- Event bus
- Validation operator
- Contracts
- Snapshots

The domain:

- Does not depend on Kafka
- Does not depend on databases
- Does not depend on web frameworks
- Does not depend on I/O

The domain implements:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

---

3.2 Application Layer
~~~~~~~~~~~~~~~~~~~~~

The Application layer contains the orchestrator:

Responsibilities:

- Instantiate domain components
- Register event subscribers
- Expose public interface
- Trigger validation after transitions

The Application layer does not implement physical laws.

---

3.3 Infrastructure Layer
~~~~~~~~~~~~~~~~~~~~~~~~

Infrastructure includes:

- Kafka adapters
- Persistence adapters
- Sensor adapters
- External APIs

Infrastructure implements Ports defined by the domain.

The domain must never import infrastructure.

---

4. Ports
--------

Ports are abstract interfaces defined by the domain.

Examples:

- ExternalEventPort
- PersistencePort
- NetworkInteractionPort

Ports define what the domain requires from the outside world.

Adapters implement these ports.

---

5. Event Bus as Domain Operator
--------------------------------

The InternalEventBus is part of the domain.

It implements the transition operator H.

It is not infrastructure.

Reasons:

- It defines causal propagation
- It guarantees determinism
- It is part of system semantics

Replacing it changes system meaning.

---

6. Dependency Rule
------------------

Dependencies must always point inward.

Infrastructure → Application → Domain

Never:

Domain → Infrastructure

Violating this rule corrupts the Digital Twin.

---

7. Why Isolation is Critical
----------------------------

Without isolation:

- External failures could corrupt state
- Concurrency could introduce non-determinism
- Infrastructure could bypass validation

Isolation guarantees:

- Determinism
- Reproducibility
- Scientific clarity

---

8. Test Strategy Implications
------------------------------

Because the domain is isolated:

- Unit tests can validate laws directly
- Integration tests can validate causal chains
- Contract tests can validate invariants

Infrastructure is tested separately.

---

9. Extension Guidelines
-----------------------

When adding a new feature:

1. Define state formally.
2. Define transition law.
3. Define invariants.
4. Implement domain logic.
5. Extend validation operator.
6. Only then implement adapters.

Never start with infrastructure.

---

10. Anti-Patterns to Avoid
--------------------------

The following are forbidden in the domain:

- Direct Kafka imports
- Direct database calls
- Async or threaded execution (MVP)
- Silent state mutation
- Implicit time progression

Violating these compromises determinism.

---

11. Relationship to Scientific Model
-------------------------------------

The Hexagonal Architecture protects the mathematical model.

The domain implements:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

Infrastructure only supplies E.

The model remains independent of technology.

---

12. Summary
-----------

The Hexagonal Architecture ensures:

- Purity of the domain
- Deterministic evolution
- Scientific auditability
- Modular extensibility

The Digital Twin is not a web service.
It is a state transition system.

Architecture exists to protect the model.