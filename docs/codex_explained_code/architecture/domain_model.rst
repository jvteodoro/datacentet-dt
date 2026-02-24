Domain Model
============

Problem Context
---------------
The twin needs explicit representations for observations, latent state, transitions, and replay.

Conceptual Tension
------------------
A minimal model is easier to validate, but practical network-flow dynamics require richer topological and flow-level structures.

Abstraction Introduced
----------------------
Two domain nuclei coexist:

1. ``digital_twin.domain`` for deterministic event transition of network-flow state.
2. ``domain.core`` for epistemic/scientific abstractions (``Observable``, ``StateVariable``, ``StateVector``, ``Snapshot``).

Formal Definition
-----------------
The transition nucleus models:

.. math::
   X = (\text{topology}, \text{link\_backlog}, \text{active\_flows}, v, n)

where :math:`v` is version counter and :math:`n` is event counter.

Implementation Strategy
-----------------------
``TwinState`` and ``NetworkTopology`` separate structural from dynamic state, while ``FlowRecord`` encodes per-flow path/rate/remaining size.

Consequences
------------
This decomposition supports local updates and deterministic replay while keeping a stable representation for snapshot projection and invariant checks.
