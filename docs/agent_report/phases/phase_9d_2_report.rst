Phase 9D.2 Report — Metrics Coverage Expansion + Cardinality Policy
====================================================================

Architectural scope
-------------------

- Extended ``MetricsSnapshot`` with bounded ``topk`` and fixed-shape
  ``histograms`` blocks.
- Added snapshot-only ``NetworkInsightProvider`` and ``ComputeInsightProvider``.
- Added cache-backed read-only endpoints: ``/metrics/top`` and
  ``/metrics/histograms``.
- Added formal policy document:
  ``docs/engineering/observability_cardinality_policy.rst``.

Determinism verification
------------------------

- Top-K ordering implemented as ``(value DESC, id ASC)``.
- Histogram bin edges are static configuration constants.
- JSON serialization uses sorted keys and deterministic category ordering.
- Observability computations consume immutable ``TwinSnapshot`` only.

Cardinality policy summary
--------------------------

- Always-on metrics remain aggregate only.
- Forbidden always-on dimensions: ``flow_id``, ``workload_id``, full entity dumps.
- Top-K bounded by ``OBS_TOPK_DEFAULT`` and ``OBS_TOPK_HARD_MAX``.
- Histogram bin counts fixed by configured edges.

Complexity analysis
-------------------

- ``/metrics`` cache-hit cost: O(1).
- ``/metrics/top`` and ``/metrics/histograms`` cache-hit cost: O(1) lookup +
  bounded payload serialization.
- Refresh cost: bounded by snapshot arrays (links/servers), with no unbounded
  per-request scans.

Known limitations
-----------------

- Top-K categories are fixed to network backlog and server resource usage.
- Histogram bins are static defaults and may require environment tuning.

Gate decision
-------------

- **Passed**
