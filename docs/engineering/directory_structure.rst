Directory Structure
===================

1. Introduction
---------------

This document explains the rationale behind the directory organization of the Data Center Digital Twin.

The directory structure is not arbitrary.

It reflects:

- The mathematical structure of the system (X, E, H, V)
- The hexagonal architecture
- The separation of concerns
- The scientific validation model
- The testing strategy

The directory layout is part of the system's integrity.

---

2. Top-Level Structure
----------------------

The project is organized as:

::

    digital_twin/
        application/
        domain/
        infrastructure/
        tests/
        docs/

Each directory corresponds to an architectural role.

---

3. Domain Directory
-------------------

The domain directory is the core of the system.

It implements:

.. math::

    (X, E, H, V)

Structure:

::

    domain/
        events/
        event_bus/
        network/
        compute/
        snapshot/
        contracts/

3.1 events/
~~~~~~~~~~~

Contains:

- Base event definition
- Network events
- Compute events

Purpose:

Defines E (event space).

Events are immutable and form the backbone of causality.

---

3.2 event_bus/
~~~~~~~~~~~~~~

Contains:

- InternalEventBus

Purpose:

Implements the transition operator H.

This is part of the domain because it defines system semantics.

---

3.3 network/
~~~~~~~~~~~~

Contains:

- QueueState
- NetworkLayer
- NetworkSnapshot

Purpose:

Implements X_net and its transition laws.

Defines flow conservation.

---

3.4 compute/
~~~~~~~~~~~~

Contains:

- TaskState
- ComputeNode
- ComputationalLayer
- ComputeSnapshot

Purpose:

Implements X_comp and its transition laws.

Defines work conservation.

---

3.5 snapshot/
~~~~~~~~~~~~~

Contains:

- DataCenterSnapshot

Purpose:

Represents the observable state of X.

Snapshots are immutable.

They are used for:

- Validation
- Replay comparison
- External visualization

---

3.6 contracts/
~~~~~~~~~~~~~~

Contains:

- Conservation contracts
- Physical limits contracts
- Temporal contracts
- Global contracts
- DomainValidator

Purpose:

Implements V (validation operator).

Contracts define normative boundaries.

---

4. Application Directory
------------------------

::

    application/
        datacenter_twin.py

Purpose:

Contains the orchestrator.

Responsibilities:

- Instantiate domain components
- Wire subscribers
- Expose ingest_event()
- Trigger validation after evolution

The Application layer does not implement physics.

---

5. Infrastructure Directory
---------------------------

::

    infrastructure/
        kafka_adapter.py
        persistence_adapter.py
        sensor_adapter.py

Purpose:

Implements external ports.

Infrastructure:

- Delivers external events
- Persists snapshots
- Interfaces with real-world systems

The domain must not import infrastructure.

---

6. Tests Directory
------------------

::

    tests/
        unit/
        integration/
        contracts/
        replay/

Structure reflects testing layers.

6.1 unit/
~~~~~~~~~

Local subsystem tests.

6.2 integration/
~~~~~~~~~~~~~~~~

Cross-layer composition tests.

6.3 contracts/
~~~~~~~~~~~~~~

Explicit invariant violation tests.

6.4 replay/
~~~~~~~~~~~

Determinism and replay verification.

Tests are organized by purpose, not by file proximity.

---

7. Documentation Directory
--------------------------

::

    docs/
        theory/
        architecture/
        engineering/
        roadmap/

Documentation mirrors conceptual layers.

Code and documentation evolve together.

---

8. Dependency Direction
-----------------------

Dependencies must flow inward:

Infrastructure → Application → Domain

Never:

Domain → Infrastructure

Tests may depend on all layers.

---

9. Rationale for Separation
---------------------------

The separation ensures:

- Deterministic domain
- Testable core
- Replaceable infrastructure
- Independent evolution of components
- Scientific clarity

Mixing responsibilities introduces:

- Hidden state
- Non-determinism
- Validation bypass
- Architectural decay

---

10. Extension Guidelines
------------------------

When adding a new subsystem:

1. Add domain model under domain/.
2. Add validation contracts under contracts/.
3. Add integration in application layer.
4. Add tests at all relevant layers.
5. Add documentation under docs/.

Never introduce new functionality directly in infrastructure.

---

11. Naming Philosophy
---------------------

Directory names reflect conceptual roles:

- network → transport physics
- compute → processing physics
- contracts → normative laws
- snapshot → observable state

Names must reflect model structure, not technology.

---

12. Summary
-----------

The directory structure reflects:

- Mathematical structure
- Architectural isolation
- Testing methodology
- Validation philosophy

It is not accidental.

It is part of the system's scientific integrity.