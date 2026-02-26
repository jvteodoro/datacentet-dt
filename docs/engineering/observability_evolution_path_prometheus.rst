Observability Evolution Path to Prometheus
==========================================

Stage 0 (current)
-----------------

CSV sidecar (psutil) + Locust CSV + local analysis scripts.

Why CSV first: local reproducibility, minimal dependencies, deterministic side-channel
telemetry with clear artifact capture.

Stage 1
-------

Prometheus scraping for Metrics API + node exporter + postgres exporter + kafka exporter.

Stage 2
-------

Grafana dashboards and alerting for p95/p99, lag, DB latency, coordinator eviction.

Stage 3
-------

CI smoke envelopes and scheduled regression runs (local-only default, opt-in).

Hyperscale limits without Prometheus
------------------------------------

- Coarse sampling and manual aggregation
- Limited retention
- Harder cross-host correlation
- Limited cardinality governance automation

CSV to Prometheus mapping
-------------------------

- ``cpu_percent`` -> ``process_cpu_percent`` (gauge)
- ``rss_bytes`` -> ``process_resident_memory_bytes``
- ``vms_bytes`` -> ``process_virtual_memory_bytes``
- ``threads`` -> ``process_threads``
- ``open_fds`` -> ``process_open_fds``
- ``read_bytes_total`` -> ``process_io_read_bytes_total``
- ``write_bytes_total`` -> ``process_io_write_bytes_total``
- ``system_cpu_percent`` -> ``node_cpu_utilization_percent``
- ``system_mem_percent`` -> ``node_memory_utilization_percent``

Determinism boundary
--------------------

Metrics remain observational side-channel only and do not participate in domain state
evolution/replay semantics.

Recommended compose additions (docs-only)
-----------------------------------------

Add optional exporters as compose services in a future phase; keep current phase
implementation unchanged.
