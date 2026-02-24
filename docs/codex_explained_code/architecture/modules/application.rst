Application Modules
===================

Problem Context
---------------
Application code must orchestrate domain kernels into runnable scenarios without redefining invariants.

Conceptual Tension
------------------
Convenience wrappers can accidentally duplicate domain policy.

Abstraction Introduced
----------------------
Application modules are integration façades (``application.datacenter_twin`` and examples) that wire queues, compute nodes, and snapshots.

Formal Definition
-----------------
Application layer is a composition operator:

.. math::
   A = \mathcal{C}(D_{network}, D_{compute}, B_{events})

Implementation Strategy
-----------------------

.. automodule:: application.datacenter_twin
   :members:
   :undoc-members:
   :show-inheritance:

Consequences
------------
Domain contracts remain centralized while scenario assembly stays explicit and replaceable.
