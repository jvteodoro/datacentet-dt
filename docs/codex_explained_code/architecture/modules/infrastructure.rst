Infrastructure Modules
======================

Problem Context
---------------
Deterministic execution requires a transport mechanism for events and reusable subsystem wiring.

Conceptual Tension
------------------
Infrastructure should provide mechanics (delivery, sequencing) without embedding domain semantics.

Abstraction Introduced
----------------------
The repository uses lightweight internal infrastructure through ``domain.event_bus.internal_event_bus`` and layer adapters in ``domain.network``/``domain.compute``.

Formal Definition
-----------------
Infrastructure is treated as deterministic mediation:

.. math::
   I: E \times \text{subscribers} \rightarrow E^*

Implementation Strategy
-----------------------

.. automodule:: domain.event_bus.internal_event_bus
   :members:
   :undoc-members:
   :show-inheritance:

Consequences
------------
The code avoids external broker dependency while preserving causal ordering assumptions needed by replay tests.
