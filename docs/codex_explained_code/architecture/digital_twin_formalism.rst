Digital Twin Formalism
======================

Problem Context
---------------
The project mixes software engineering constraints with scientific state estimation terms; a shared formal vocabulary is necessary.

Conceptual Tension
------------------
Without formal definitions, contract reasoning becomes implementation-dependent.

Abstraction Introduced
----------------------
Core entities are defined as mathematical objects and mapped to code artifacts.

Formal Definition
-----------------

.. math::
   \textbf{Observable } o_t = (n, v, u, c, t, s)

.. math::
   \textbf{StateVariable } x_t = (n, \hat{v}, \hat{u}, t)

.. math::
   \textbf{StateVector } X_t = [x_t^1, \dots, x_t^k], \quad \Sigma_t \succeq 0

.. math::
   \textbf{ObservationModel } g: X_t \rightarrow \hat{o}_t

.. math::
   \textbf{StateEstimator } f: (X_{t-1}, o_t, \theta) \mapsto X_t

.. math::
   \textbf{ParameterIdentifier } p: (o_{1:t}, X_{1:t}) \mapsto \theta_t

.. math::
   \textbf{Snapshot } \sigma_t = \Pi(X_t, o_t, \theta_t)

.. math::
   \textbf{Validator } \mathcal{V}(\sigma_t) \in \{\top, \bot\}

Implementation Strategy
-----------------------
``domain.core`` hosts most epistemic abstractions; ``digital_twin.domain`` provides operational transition semantics and replay.

Consequences
------------
Formal names become traceability anchors between tests, contracts, and architecture decisions.
