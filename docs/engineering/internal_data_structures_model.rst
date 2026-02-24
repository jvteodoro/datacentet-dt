Internal Data Structures Model
==============================

1. Purpose
----------

This document defines the internal data structures of the Digital Twin Core.

The goal is to:

- Preserve hyperscale scalability
- Maintain deterministic behavior
- Enable sparse updates
- Support replay
- Minimize memory overhead
- Avoid global scans

The internal representation must reflect the formal state:

.. math::

   X_t =
   \begin{bmatrix}
   G_{net,t} \\
   G_{comp,t} \\
   \Phi_t
   \end{bmatrix}

---

2. Design Principles
--------------------

1. Sparse representation only
2. Local updates only
3. No implicit iteration over all nodes
4. Immutable topology where possible
5. Delta-based mutation tracking
6. Minimal object allocation
7. Deterministic ordering

---

3. Network Topology Representation
-----------------------------------

3.1 Static Topology Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Topology must be immutable after initialization (except via explicit events).

Use compact adjacency representation:

::

    node_index: Dict[str, int]
    reverse_node_index: List[str]
    adjacency: List[Tuple[int]]

- node_index maps node_id → integer index
- adjacency[i] contains neighbor indices
- reverse_node_index allows reverse lookup

Integer indexing reduces memory and improves performance.

---

3.2 Link Storage
~~~~~~~~~~~~~~~~~

Links must be stored in flat arrays.

::

    link_capacity: Array[float]
    link_latency: Array[float]
    link_utilization: Array[float]
    link_backlog: Array[float]

Link indexing:

::

    link_index: Dict[(src_idx, dst_idx), int]

No Link objects per edge.

Flat arrays minimize overhead.

---

4. Active Flow Representation
-----------------------------

Flows are dynamic and sparse.

Store only active flows:

::

    flow_source: Dict[flow_id, int]
    flow_destination: Dict[flow_id, int]
    flow_rate: Dict[flow_id, float]
    flow_remaining: Dict[flow_id, float]
    flow_path: Dict[flow_id, Tuple[int]]

No global flow list scan allowed.

To update a link:

- Maintain mapping link → active flow ids

::

    link_active_flows: Dict[int, Set[flow_id]]

This allows O(flows_on_link) updates.

---

5. Compute Cluster Representation
----------------------------------

5.1 Server Indexing
~~~~~~~~~~~~~~~~~~~~

Similar to network:

::

    server_index: Dict[str, int]
    reverse_server_index: List[str]

---

5.2 Resource Arrays
~~~~~~~~~~~~~~~~~~~~

Use flat arrays:

::

    cpu_capacity: Array[float]
    cpu_load: Array[float]
    memory_capacity: Array[float]
    memory_load: Array[float]

Avoid per-server objects.

---

5.3 Workload Mapping
~~~~~~~~~~~~~~~~~~~~

Active workloads:

::

    workload_server: Dict[workload_id, int]
    workload_cpu_remaining: Dict[workload_id, float]
    workload_memory: Dict[workload_id, float]

No scanning over all workloads.

Maintain per-server workload list:

::

    server_active_workloads: Dict[int, Set[workload_id]]

---

6. Workload Profile Storage
----------------------------

Statistical profile is small.

::

    arrival_rate: Dict[class_id, float]
    mean_cpu: Dict[class_id, float]
    mean_memory: Dict[class_id, float]
    burstiness: Dict[class_id, float]

Profile updates are infrequent.

---

7. Delta Tracking for Snapshots
--------------------------------

To avoid copying full state:

Maintain mutation registry:

::

    modified_links: Set[int]
    modified_servers: Set[int]
    modified_flows: Set[flow_id]
    modified_workloads: Set[workload_id]

Snapshot generation uses:

- Static topology reference
- Current arrays
- Modified entity list

Optional: version counter per entity.

---

8. Deterministic Ordering
--------------------------

All iteration must use:

- Sorted integer indices
- Stable ordering of flow_ids
- No unordered set iteration affecting state

When iterating sets:

::

    for fid in sorted(flow_ids):

Determinism must be preserved.

---

9. Event Update Complexity
---------------------------

Per-event operations must satisfy:

.. math::

   O(|affected\_entities|)

Examples:

- FlowStarted → update path links only
- LinkUtilizationUpdate → update single link
- WorkloadStarted → update one server

No full topology scans allowed.

---

10. Memory Efficiency Constraints
----------------------------------

Memory footprint must scale with:

- Active flows
- Active workloads
- Number of links
- Number of servers

Avoid:

- Nested object graphs
- Deep object trees
- Excessive wrapper classes

Prefer:

- Flat arrays
- Integer indices
- Compact mappings

---

11. Concurrency Considerations
------------------------------

Domain core remains single-threaded.

Parallelism may exist:

- In ingestion partitions
- In inference
- In optimization

Domain must not use locks.

---

12. Serialization Strategy
--------------------------

Snapshot serialization must:

- Serialize flat arrays
- Serialize active entity dictionaries
- Not serialize adjacency repeatedly
- Use compact binary format (outside domain)

Serialization logic belongs to infrastructure.

---

13. Performance Guarantees
---------------------------

Given:

- N nodes
- E links
- F active flows
- S servers
- W workloads

Per-event complexity must satisfy:

.. math::

   O(\max(F_{local}, W_{local}))

Not:

.. math::

   O(N + E + S)

---

14. Extension Guidelines
------------------------

New subsystem must:

- Use integer indexing
- Avoid per-entity object creation
- Follow flat-array principle
- Preserve sparse updates
- Preserve deterministic ordering

---

15. Summary
-----------

The internal data structure model ensures:

- Hyperscale viability
- Sparse updates
- Deterministic replay
- Efficient memory usage
- Low-latency event processing
- Compatibility with inference and optimization

It transforms the formal flow-level model into an implementable high-performance system.

Architecture Alignment Note
---------------------------

This document conforms to the canonical model:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

It preserves the determinism rule: identical initial state and identical ordered event sequence must produce identical final state and validation outcomes.

