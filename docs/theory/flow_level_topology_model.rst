Flow-Level Topology Model
=========================

1. Introduction
---------------

This document formally defines the flow-level model used by the Data Center Digital Twin.

The system is designed for:

- Hyperscale environments
- Real-time state reconstruction
- Strategic optimization
- Efficient computation
- Deterministic replay

The Digital Twin operates at the **flow level**, not packet level.

The objective is to provide a computationally tractable yet physically meaningful representation of large-scale data center networks and compute clusters.

---

2. Design Principles
--------------------

The flow-level model follows these principles:

1. Aggregated representation (no packet simulation)
2. Sparse state evolution
3. Event-driven updates
4. Deterministic transitions
5. Scalable to 10^4–10^6 nodes
6. Compatible with online inference and optimization

The system remains defined as:

.. math::

   DigitalTwin = (X, E, H, V)

Where:

- X = global state
- E = event space
- H = deterministic transition operator
- V = validation operator

---

3. Network Model (Flow-Level Graph)
------------------------------------

3.1 Topological Structure
~~~~~~~~~~~~~~~~~~~~~~~~~

The network is represented as a directed graph:

.. math::

   G_{net} = (V, E)

Where:

- V = network nodes (switches, routers, ToR, spine, leaf)
- E = physical links

The graph may dynamically evolve via SDN events.

---

3.2 Link State Representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each link :math:`e \in E` has:

- Capacity :math:`C_e`
- Base latency :math:`L_e`
- Utilization :math:`u_e(t)`
- Backlog :math:`q_e(t)`

State vector per link:

.. math::

   X_e(t) = (C_e, L_e, u_e(t), q_e(t))

---

3.3 Flow Representation
~~~~~~~~~~~~~~~~~~~~~~~

A flow is defined as:

.. math::

   f = (src, dst, r_f(t), s_f(t), class)

Where:

- src = source node
- dst = destination node
- r_f(t) = instantaneous rate
- s_f(t) = remaining size
- class = workload class

Flows are aggregates of packets.

---

3.4 Flow Evolution Law
~~~~~~~~~~~~~~~~~~~~~~

For a link e:

.. math::

   q_e(t+\Delta t) =
   \max\left(
   0,
   q_e(t)
   + \sum_{f \in e} r_f(t)\Delta t
   - C_e \Delta t
   \right)

This preserves aggregated flow conservation.

No packet-level simulation is performed.

---

3.5 Network-Level Conservation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the entire network:

.. math::

   \sum ingress = \sum egress + \sum backlog

This invariant must always hold.

---

4. Compute Cluster Model
------------------------

4.1 Cluster Structure
~~~~~~~~~~~~~~~~~~~~~

The compute subsystem is represented as:

.. math::

   G_{comp} = (S, R)

Where:

- S = set of servers
- R = resource types (CPU, memory, storage)

---

4.2 Server State Representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each server i maintains:

- CPU capacity :math:`\mu_i`
- Memory capacity :math:`M_i`
- Current CPU load :math:`cpu_i(t)`
- Current memory usage :math:`mem_i(t)`

State vector per server:

.. math::

   X_i(t) = (\mu_i, M_i, cpu_i(t), mem_i(t))

---

4.3 Workload Representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A workload is defined as:

.. math::

   w = (arrival\_time, cpu\_demand, memory\_demand, duration, class)

Workloads are treated as aggregated resource consumers.

---

4.4 Compute Evolution Law
~~~~~~~~~~~~~~~~~~~~~~~~~~

For server i:

.. math::

   cpu_i(t+\Delta t) =
   \min\left(
   \mu_i,
   cpu_i(t)
   + incoming\_load
   - completed\_load
   \right)

Memory evolves similarly under capacity constraints.

---

5. Workload Profile Model
--------------------------

5.1 Workload Classes
~~~~~~~~~~~~~~~~~~~~

Each workload belongs to a class c:

- Latency-sensitive
- Throughput-oriented
- Batch
- ML-training
- Interactive

Each class has statistical characteristics.

---

5.2 Statistical Profile Vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define workload profile vector:

.. math::

   \Phi =
   (\lambda_c,
    E[cpu_c],
    E[mem_c],
    E[flow\_size_c],
    burstiness_c)

Where:

- :math:`\lambda_c` = arrival rate
- E[...] = expected demand
- burstiness = variability indicator

The profile evolves over time.

---

6. Global State Definition
--------------------------

The global state is defined as:

.. math::

   X_t =
   \begin{bmatrix}
   G_{net,t} \\
   G_{comp,t} \\
   \Phi_t
   \end{bmatrix}

The state must be sufficient to:

- Reconstruct congestion
- Reconstruct utilization
- Support replay
- Enable inference
- Enable optimization

---

7. Metrics for Strategic Analysis
----------------------------------

Define global metric vector:

.. math::

   M_t =
   (
   network\_utilization,
   compute\_utilization,
   congestion\_ratio,
   latency\_percentiles,
   SLA\_violation\_rate,
   fairness\_index
   )

These metrics are derived from state.

They do not modify state.

---

8. Temporal Scales
------------------

The system operates on two time scales:

Micro-scale:
    Event-driven updates

Macro-scale:
    Window-based metric aggregation
    Inference updates
    Optimization decisions

This separation ensures stability and efficiency.

---

9. Computational Complexity
---------------------------

State updates are:

.. math::

   O(|flows\_affected|)

Not:

.. math::

   O(|V| + |E|)

The model is sparse and event-driven.

Only active flows and affected links are updated.

---

10. Determinism and Replay
--------------------------

Given identical:

- Initial state
- Event sequence

The flow-level model must produce identical results.

All flow updates are deterministic.

No stochastic behavior is allowed in the domain layer.

---

11. Interaction with Inference and Optimization
-----------------------------------------------

The flow-level model defines X_t.

Inference and optimization operate on X_t but do not modify H.

Inference:

.. math::

   \theta_{t+1} = \mathcal{I}(X_t, Y_t)

Optimization:

.. math::

   u_t = \mathcal{O}(X_t, \theta_t)

They are external to the core domain.

---

12. Scope Limitations
---------------------

The flow-level model intentionally excludes:

- Packet-level retransmissions
- TCP window dynamics
- Instruction-level CPU modeling
- Power electronics detail

The objective is strategic modeling, not micro-simulation.

---

13. Summary
-----------

The flow-level topology model provides:

- A scalable representation of hyperscale networks
- A scalable representation of compute clusters
- Workload-aware modeling
- Deterministic state evolution
- Compatibility with real-time ingestion
- Compatibility with inference and optimization

This model replaces the single-queue MVP model.

It is the foundation for hyperscale Digital Twin operation.
