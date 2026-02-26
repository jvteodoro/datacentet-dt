Hardware Telemetry CSV Sidecar
==============================

``load_testing/telemetry/resource_sidecar.py`` samples process-level CPU, memory,
thread count, open FDs, and IO counters into ``resource_usage.csv``.
Unsupported fields are written as empty cells.

Default sampling interval is 0.5s and configurable by
``RESOURCE_SAMPLING_INTERVAL_S``.

Schema source of truth: ``load_testing/telemetry/csv_schema.md``.

For long-term evolution, see :doc:`observability_evolution_path_prometheus`.
