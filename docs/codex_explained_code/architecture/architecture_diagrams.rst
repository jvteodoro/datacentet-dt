Architecture Diagrams
=====================

Problem Context
---------------
Architecture claims require executable diagrams instead of static images.

Conceptual Tension
------------------
Narrative documentation can drift from code unless diagrams are generated from modules and controlled graph definitions.

Abstraction Introduced
----------------------
Sphinx Graphviz and inheritance directives render structure during build.

Formal Definition
-----------------
Diagrams act as projection functions :math:`\Delta: \text{code} \rightarrow \text{graph}`.

Implementation Strategy
-----------------------

Domain class hierarchy
^^^^^^^^^^^^^^^^^^^^^^

.. inheritance-diagram:: digital_twin.domain digital_twin.domain.twin.DataCenterTwin
   :parts: 2

Snapshot semantics
^^^^^^^^^^^^^^^^^^

.. graphviz::

   digraph SnapshotSemantics {
       rankdir=LR;
       Measurement -> Estimator -> Snapshot -> Validator -> ValidationReport;
   }

Domain graph
^^^^^^^^^^^^

.. graphviz:: diagrams/domain_graph.dot

Validator graph
^^^^^^^^^^^^^^^

.. graphviz:: diagrams/validator_graph.dot

Dependency graph
^^^^^^^^^^^^^^^^

.. graphviz:: diagrams/dependency_graph.dot

Consequences
------------
Build-time rendering ties architecture evidence to concrete source modules and controlled dependency assumptions.
