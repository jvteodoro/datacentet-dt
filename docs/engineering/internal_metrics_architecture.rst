Internal Metrics Architecture
=============================

1. Purpose
----------

This document defines the internal metrics architecture of the Digital Twin.

Metrics must:

- Be lightweight
- Be deterministic
- Avoid memory overhead
- Avoid locking inside domain
- Avoid global scans
- Be safe under hyperscale load

Metrics must not interfere with domain semantics.

---

2. Architectural Principles
---------------------------

1. Metrics are observational only.
2. Metrics must not mutate domain state.
3. Metrics must not influence H or V.
4. Metrics must not allocate per event.
5. Metrics must not perform global scans.
6. Metrics collection must be O(1) per event.

---

3. Metrics Layer Separation
---------------------------

Metrics live outside domain logic.

Structure:

::

    Digital Twin Core
        ↓
    Metrics Collector (hooked at boundary)
        ↓
    Metrics Export Adapter

The domain exposes events such as:

- event_processed
- snapshot_generated
- inference_completed
- optimization_completed

Metrics layer subscribes but never injects.

---

4. Metrics Categories
---------------------

4.1 Event Metrics
~~~~~~~~~~~~~~~~~

- events_processed_total
- event_processing_latency
- events_per_second

4.2 Snapshot Metrics
~~~~~~~~~~~~~~~~~~~~

- snapshot_generation_latency
- snapshot_count

4.3 Inference Metrics
~~~~~~~~~~~~~~~~~~~~~

- inference_latency
- inference_update_count

4.4 Optimization Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~

- optimization_latency
- optimization_action_count

4.5 State Metrics
~~~~~~~~~~~~~~~~~

- active_flows_count
- active_workloads_count
- active_links_count
- active_servers_count

State metrics must use maintained counters.
Never compute via scanning.

---

5. Latency Measurement Strategy
--------------------------------

Latency must be measured using:

::

    start = monotonic_time()
    process_event()
    end = monotonic_time()

Only measure at ingestion boundary.

Do not measure inside domain logic.

Latency measurement must be:

- Constant time
- No object allocation
- No histogram per event

Histograms computed outside domain.

---

6. Counter Implementation
--------------------------

Counters must use simple integers:

::

    self.events_processed += 1

Avoid:

- Atomic operations inside domain
- Thread synchronization
- Lock contention

Domain is single-threaded.

---

7. Active Entity Counters
--------------------------

Active entity counters must be updated incrementally.

Example:

When FlowStarted:
    active_flows_count += 1

When FlowEnded:
    active_flows_count -= 1

Never compute:

::

    len(flow_dict)

inside load loop.

---

8. Memory Usage Tracking
------------------------

Memory metrics must be collected outside domain using:

- OS-level process monitoring
- Runtime memory measurement

Domain must not introspect memory.

---

9. Metrics Export Interface
---------------------------

Metrics layer must expose:

- HTTP endpoint (/metrics)
- JSON snapshot
- Optional Prometheus format

Export must be asynchronous and outside domain.

---

10. Sampling Strategy
---------------------

Under very high load:

- Not every event latency must be stored.
- Use sampling (e.g., 1 in N events).
- Sampling must be deterministic if required.

Sampling must occur in metrics layer,
never inside domain logic.

---

11. Performance Constraints
---------------------------

Per-event metrics overhead must satisfy:

::

    O(1)

Added latency must be:

    ≤ 2% of event processing time.

If metrics overhead exceeds 5%,
instrumentation must be revised.

---

12. Determinism Constraints
---------------------------

Metrics must not:

- Affect event ordering
- Affect state mutation
- Affect snapshot content

Metrics must not be persisted in event log.

Replay must ignore metrics.

---

13. Load Testing Integration
----------------------------

Locust must consume metrics from:

- HTTP endpoint
- JSON export
- Log file

Metrics must include:

- p50 latency
- p95 latency
- p99 latency
- throughput
- active flows
- memory usage

---

14. Failure Conditions
----------------------

Metrics system is considered faulty if:

- Latency overhead exceeds threshold
- Counters drift from actual state
- Export blocks ingestion
- Memory grows unbounded

Metrics must fail independently,
not crash domain core.

---

15. Summary
-----------

The internal metrics architecture ensures:

- Minimal overhead
- Hyperscale compatibility
- Deterministic isolation
- Efficient load testing
- Safe performance monitoring

Metrics must observe the system,
never influence it.

Architecture Alignment Note
---------------------------

This document conforms to the canonical model:

.. math::

   System = (X, E, H, V, \mathcal{I}, \mathcal{O})

It preserves the determinism rule: identical initial state and identical ordered event sequence must produce identical final state and validation outcomes.

