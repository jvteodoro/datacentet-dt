Trade-offs
==========

Problem Context
---------------
The architecture optimizes determinism, validity, and operational performance simultaneously.

Conceptual Tension
------------------
These goals are partially antagonistic: stronger immutability and richer validation often cost memory and CPU.

Abstraction Introduced
----------------------
Three major balancing mechanisms are visible: local validation scopes, rollback-protected mutation, and immutable snapshot boundaries.

Formal Definition
-----------------
A simplified optimization lens:

.. math::
   \min \; C_{runtime}(H, V) \quad \text{s.t.} \quad D_{replay}=0,\; I_{contracts}=\top

Implementation Strategy
-----------------------
- Keep validator loops local to modified entities.
- Permit in-place internal mutation only with reversible actions.
- Preserve immutable snapshots and copied external state views.

Consequences
------------
The system trades implementation simplicity for better asymptotic behavior in practical flow-heavy scenarios while preserving deterministic external semantics.
