Data Center Digital Twin Documentation
======================================

System philosophy
-----------------

The project is a determinism-first, event-sourced digital twin for hyperscale data center reasoning.

Canonical formal model:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

High-level architecture diagram
-------------------------------

::

    +---------------------+      +------------------+
    | Infrastructure      | ---> | Ingestion        |
    | (sensors, streams)  |      | (normalize/order)|
    +---------------------+      +---------+--------+
                                            |
                                            v
                                  +---------+--------+
                                  | Domain Core      |
                                  | (X, E, H, V)     |
                                  +----+--------+----+
                                       |        |
                                       v        v
                               +-------+--+  +--+----------------+
                               | Inference |  | Persistence       |
                               |   𝓘       |  | event log/snapshot|
                               +-----+-----+  +-------------------+
                                     |
                                     v
                               +-----+-----+
                               | Optimization|
                               |     𝓞       |
                               +-----+------+
                                     |
                                     v
                                control events
                                     |
                                     +--> ingestion

Key references
--------------

- Architecture blueprint: :doc:`architecture/system_blueprint`
- Performance budget: :doc:`engineering/performance_budget`
- Implementation roadmap: :doc:`engineering/implementation_roadmap`

Navigation
----------

.. toctree::
   :maxdepth: 2
   :caption: Theory

   theory/index

.. toctree::
   :maxdepth: 2
   :caption: Architecture

   architecture/index

.. toctree::
   :maxdepth: 2
   :caption: Engineering

   engineering/index

.. toctree::
   :maxdepth: 2
   :caption: Agent Reporting

   agent_report/index

.. toctree::
   :maxdepth: 2
   :caption: Performance

   performance/index

.. toctree::
   :maxdepth: 2
   :caption: Testing

   testing/index

.. toctree::
   :maxdepth: 2
   :caption: Documentation Structure

   structure/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
