Domain Modules
==============

Problem Context
---------------
Domain code must encode deterministic state evolution and scientific contract primitives without framework coupling.

Conceptual Tension
------------------
The repository contains two domain strata (``digital_twin.domain`` and ``domain.core``), which can blur responsibilities.

Abstraction Introduced
----------------------
- ``digital_twin.domain``: operational deterministic transition engine.
- ``domain.core``: epistemic primitives used by contract-oriented validation.

Formal Definition
-----------------
Domain invariants include non-negative counters, bounded link backlog, and non-negative flow parameters.

Implementation Strategy
-----------------------

.. automodule:: digital_twin.domain.snapshot
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: digital_twin.domain.transition
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: digital_twin.domain.validation
   :members:
   :undoc-members:
   :show-inheritance:

Consequences
------------
The domain layer remains testable as pure transition/validation logic with replay-centric semantics.
