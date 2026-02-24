Validator Architecture
======================

Problem Context
---------------
The system needs deterministic acceptance/rejection with explicit attribution of violations.

Conceptual Tension
------------------
A monolithic validator centralizes policy but can obscure contract provenance.

Abstraction Introduced
----------------------
``Validator`` acts as a coordinator, while each contract module remains a separate proof obligation.

Formal Definition
-----------------
For snapshot :math:`\sigma`, validator output is:

.. math::
   R(\sigma) = (\text{is\_valid}, \{(c_i, \epsilon_i)\})

Implementation Strategy
-----------------------
The orchestrator executes contracts in fixed order and records violations in a per-contract dictionary.

.. graphviz::

   digraph ValidatorStratification {
       rankdir=TB;
       Software -> Temporal;
       Temporal -> Statistical;
       Statistical -> Epistemic;
       Epistemic -> Model;
       Model -> Hierarchy;
   }

Consequences
------------
Order is explicit and reproducible; diagnostics preserve semantic locality of failure.
