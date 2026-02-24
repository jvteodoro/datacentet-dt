Architecture Overview
=====================

Problem Context
---------------
The project needs deterministic replay, formally constrained validation, and explicit separation between state transition and scientific contract checking.

Conceptual Tension
------------------
Event-sourced systems favor append-only simplicity, while flow-level simulation requires mutable performance-sensitive structures.

Abstraction Introduced
----------------------
A layered architecture is used: domain transition core (``digital_twin.domain``), contract validator core (``domain.validation`` + ``domain.contracts``), and orchestration/application façades.

Formal Definition
-----------------
The architecture instantiates a discrete-time transition system with validated commits:

.. math::
   X_{t+1} = H(X_t, e_t) \quad \text{accepted only if} \quad V(X_{t+1}) = \top

Implementation Strategy
-----------------------
The ingestion order in ``DataCenterTwin.ingest_event`` is fixed: normalize :math:`\rightarrow` transition :math:`\rightarrow` validate :math:`\rightarrow` commit :math:`\rightarrow` snapshot :math:`\rightarrow` metrics.

.. code-block:: python

   normalized_event = self._normalizer_fn(event)
   candidate = self._transition_fn(self._state, normalized_event)
   self._validator_fn(candidate)
   self._state = candidate.state if isinstance(candidate, TransitionCandidate) else candidate

Consequences
------------
Determinism is promoted to an architectural invariant, and rollback in ``TransitionCandidate`` turns validation failure into a non-committing branch rather than a partially applied mutation.
