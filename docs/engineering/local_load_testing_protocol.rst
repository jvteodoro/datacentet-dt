Local Load Testing Protocol
===========================

1. Purpose
----------

This document defines the protocol for performing load testing locally
using Locust while keeping Codex responsible only for code generation.

Codex must not execute load tests.
All load testing is performed in a local controlled environment.

Results are analyzed separately.

---

2. Responsibility Split
-----------------------

Codex responsibilities:

- Generate fully functional system code.
- Expose metrics endpoints.
- Provide logging hooks.
- Provide Locust example script.
- Ensure instrumentation is enabled.

User responsibilities:

- Execute Locust locally.
- Run sustained load tests.
- Collect metrics output.
- Export structured logs.
- Share results for analysis.

---

3. Required Instrumentation
---------------------------

The Digital Twin must expose:

- event_processing_latency
- snapshot_latency
- inference_latency
- optimization_latency
- active_flows_count
- active_workloads_count
- memory_usage
- cpu_usage

Metrics must be exportable via:

- HTTP endpoint (e.g., /metrics)
- JSON export
- CSV log file

---

4. Load Testing Procedure
-------------------------

Step 1:
    Start Digital Twin system locally.

Step 2:
    Run Locust with defined load profile.

Step 3:
    Sustain load for at least 30 minutes.

Step 4:
    Collect:

        - p50 latency
        - p95 latency
        - p99 latency
        - memory usage over time
        - CPU usage
        - throughput

Step 5:
    Persist event log.

Step 6:
    Replay event log offline.

Step 7:
    Compare final snapshot.

---

5. Required Output Format
--------------------------

Results must be exported as:

- CSV (latency histogram)
- JSON (metric summary)
- Memory usage timeline
- Replay validation result (true/false)

---

6. Performance Evaluation Criteria
-----------------------------------

Results must be evaluated against performance_budget.rst.

If any metric exceeds threshold:

- Identify subsystem
- Provide event type distribution
- Provide active entity count

---

7. Failure Escalation
---------------------

If failure occurs:

1. Capture event sample.
2. Capture state size.
3. Capture modified entities count.
4. Provide metrics snapshot.

Analysis will determine:

- Complexity violation
- Memory leak
- Lock contention
- Inefficient data structure
- Contract revalidation cost

---

8. Determinism Validation
--------------------------

Replay must produce identical final snapshot.

If mismatch:

- Provide event sequence length.
- Provide last 10 events.
- Provide diff summary.

Determinism violation is critical failure.

---

9. Optimization Cycle
---------------------

Iteration loop:

1. Run load test.
2. Collect metrics.
3. Share metrics.
4. Receive architecture refinement.
5. Regenerate module via Codex.
6. Re-run load test.

Repeat until performance budget is satisfied.

---

10. Summary
-----------

This protocol ensures:

- Efficient credit usage.
- Local performance control.
- Deterministic validation.
- Scalable refinement cycle.
- Engineering rigor.
