Design Principles
=================

Problem Context
---------------
The codebase must satisfy scientific validity (contracts), software robustness (immutability/typing), and operational replayability.

Conceptual Tension
------------------
Rigid immutability increases auditability but can increase allocation cost in high-frequency flow updates.

Abstraction Introduced
----------------------
The project combines **logical immutability** at boundaries (snapshots, exposed state copies) with **controlled internal mutation** and rollback.

Formal Definition
-----------------
Let :math:`\partial X` be modified entities only. Validation locality is:

.. math::
   V(X) = \bigwedge_{i \in \partial X_{links}} C_i \land \bigwedge_{f \in \partial X_{flows}} F_f

Implementation Strategy
-----------------------
- ``TransitionCandidate`` records modified links/flows and rollback actions.
- ``validate_state`` inspects only ``modified_link_indices`` and ``modified_flow_ids``.
- ``build_snapshot`` converts dynamic lists to immutable tuples.

Consequences
------------
The architecture keeps deterministic semantics while reducing unnecessary global scans and preserving external immutability guarantees.
