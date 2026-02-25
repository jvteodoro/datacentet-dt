Optimization Architecture
=========================

Problem Context
---------------

The digital twin's physical ontology evolves strictly via event-driven state transition:

.. math::

   X_{t+1} = H(X_t, e_t)

Phase 7 introduces a decision/action layer that computes candidate control recommendations
from immutable state snapshots and inferred parameters.

Conceptual Tension
------------------

- Optimization must react to operational pressure (for example high backlog).
- The twin must remain replayable and deterministic under live and replay execution.
- Hyperscale constraints prohibit global scans over all links/servers during proposal generation.
- Optimization cannot directly mutate physical state.

Abstraction Introduced
----------------------

A modular optimization subsystem is introduced with:

- ``OptimizationStrategy`` contract for pluggable deterministic policies.
- ``OptimizationEngine`` orchestrator with mode semantics (``LIVE``, ``REPLAY``, ``DISABLED``).
- ``StrategyRegistry`` with deterministic strategy ordering.
- Immutable ``ActionProposal`` values.
- Safety/admissibility contracts for action validation.

Formal Definition
-----------------

.. math::

   a_t = \mathcal{O}(X_t, \theta_t)

where:

- :math:`X_t` is the immutable twin snapshot.
- :math:`\theta_t` is the immutable inferred parameter set.
- :math:`a_t` is a finite ordered action proposal set.

Action re-entry rule:

.. math::

   e^{control}_t = \mathrm{encode}(a_t),\quad X_{t+1} = H(X_t, e^{control}_t)

Control actions re-enter as ``ControlActionProposed`` domain events to preserve replayability.

Implementation Strategy
-----------------------

- Strategies are registered and executed in sorted strategy-id order.
- Each strategy proposes actions from aggregated active metrics only.
- Baseline strategy is O(1): when ``snapshot.total_backlog`` exceeds threshold, propose a
  ``rate_limit`` action for ingestion; otherwise emit no action.
- Every action is validated before emission:

  - timestamp equals ``snapshot.version_counter``
  - deterministic non-empty ``action_id``
  - recognized action kind
  - finite primitive payload values
  - finite expected effect values

- The optimization engine exposes action proposals and canonical conversion to
  ``ControlActionProposed`` domain events.

Consequences
------------

- Replayability is preserved because optimization re-enters through normal event ingestion.
- Domain physical state remains protected from direct optimization mutation.
- Safety contracts provide fail-fast guarantees (no partial emission when validation fails).
- The strategy architecture is open for future scheduling/routing/rate-limit policies.
- Hyperscale safety is preserved by constraining baseline complexity to O(1) time and O(1) memory.
