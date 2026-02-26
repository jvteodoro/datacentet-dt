Local Load Testing: Hyperscale Ingestion
========================================

This guide defines Phase 9E.2–9E.5 local-first campaigns for hyperscale ingestion.

Run matrix
----------

- Domain-only (in-memory persistence)
- DB events only
- DB + snapshots
- HTTP vs Kafka equivalent workloads
- Kafka rebalance/partition stress

Always keep ``SEED`` and profile fixed when comparing scenarios.

See also :doc:`hardware_telemetry_csv_sidecar` and
:doc:`observability_evolution_path_prometheus`.
