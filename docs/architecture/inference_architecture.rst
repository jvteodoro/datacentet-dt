Inference Architecture
======================

Problem Context
---------------

The deterministic twin already evolves physical state by:

.. math::

   X_{t+1} = H(X_t, e_t)

Phase 6 introduces an epistemological layer that estimates latent parameters
without modifying the physical ontology.

Conceptual Tension
------------------

- The domain engine must remain deterministic and physically grounded.
- Inference must adapt online to new evidence.
- Hyperscale constraints prohibit global scans over all entities.

Abstraction Introduced
----------------------

A dedicated inference subsystem consumes immutable ``TwinSnapshot`` values and
produces immutable parameter vectors through pluggable strategies.

Formal Definition
-----------------

.. math::

   \theta_{t+1} = f(\theta_t, g(X_t))

where :math:`g(X_t)` is observation extraction from the immutable snapshot.

Implementation Strategy
-----------------------

- **Strict separation**: inference reads ``TwinSnapshot`` only; no domain
  mutation path exists.
- **Strategy pattern**: ``InferenceStrategy`` defines initialize/update/get APIs,
  enabling new estimators (EKF, UKF, particle filters) without engine edits.
- **Deterministic engine orchestration**: strategies execute in sorted strategy-id
  order.
- **Contracts**: each ``ParameterVector`` is validated for finite values,
  covariance consistency, and timestamp monotonicity.
- **Online moving average baseline**: incremental mean update

  .. math::

     \mu_{t+1} = \mu_t + \frac{x_{t+1} - \mu_t}{n}

  with ``O(active_metrics)`` time and ``O(1)`` memory.

Consequences
------------

- Deterministic replay now covers both physical and epistemic trajectories.
- Hyperscale safety is preserved through active-entity metric extraction.
- The architecture is open for future Bayesian and filtering strategies.
- Immutable parameter vectors provide a clear read boundary for downstream
  optimization/control consumers.

Replay Semantics
----------------

Inference execution is controlled by ``InferenceMode``:

- ``LIVE``: inference executes during live operation.
- ``REPLAY``: inference executes during replay and recomputes the same outputs for the same snapshot stream.
- ``DISABLED``: inference execution is skipped and epistemic state remains unchanged.

These semantics guarantee that epistemic replay determinism is explicitly configurable
without coupling to physical transition logic.

Timestamp Formalization
-----------------------

The canonical timestamp source is:

.. math::

   \text{ParameterVector.timestamp} = \text{TwinSnapshot.version\_counter}

Monotonicity is enforced by epistemic contracts at engine boundaries.

Hyperscale Metric Extraction Policy
-----------------------------------

MovingAverageStrategy operates exclusively on aggregated active metrics,
 guaranteeing O(active) update complexity.

Allowed inputs are aggregated fields from ``TwinSnapshot`` such as:

- ``total_backlog``
- ``active_link_count``
- ``active_server_count``
- ``total_cpu_usage``

Full-array scans over ``link_backlog``, ``cpu_usage``, or workload maps are forbidden in this strategy.

Epistemic Persistence Interface
-------------------------------

Inference persistence is abstracted by ``ParameterStore``:

- ``append(parameter_vector)`` for validated immutable parameter writes
- ``load_all()`` for deterministic ordered reads

No concrete database adapter is required in this phase; the interface exists to keep
inference persistence extensible and decoupled.
