Contracts Architecture
======================

Problem Context
---------------
A digital twin must distinguish between software-level consistency and scientific validity.

Conceptual Tension
------------------
Single-pass validation is fast, but contract heterogeneity (software, temporal, statistical, epistemic, model, hierarchy) requires differentiated semantics.

Abstraction Introduced
----------------------
A stratified contract stack in ``domain.contracts`` with a unified orchestrator ``domain.validation.validator.Validator``.

Formal Definition
-----------------
Validation is defined as a conjunction over contract families:

.. math::
   \mathcal{V}(S) = SW(S) \land T(S) \land S_t(S) \land E(S) \land M(S) \land H(S)

Implementation Strategy
-----------------------
Each contract consumes a dedicated ``Snapshot`` projection (e.g., ``to_temporal_view``), and violations are aggregated into ``ValidationResult``.

Consequences
------------
This design yields traceable failure semantics and enables targeted strengthening of specific contracts without rewriting the validator orchestrator.
