Phase 9E Report — Local Locust Load Testing for Metrics API
============================================================

Summary
-------

Phase 9E introduces a complete, local-first load-testing suite for the
observability Metrics API endpoints using Locust.

Components Introduced
---------------------

- ``load_testing/locust/locustfile.py``
  - HttpUser implementation with profile-driven traffic generation.
- ``load_testing/locust/profiles.py``
  - deterministic profile catalog and environment parsing for weights/runtime.
- ``load_testing/locust/config.example.env``
  - ready-to-edit defaults for local campaigns.
- ``load_testing/locust/README.md``
  - quick-start + profile usage.
- ``load_testing/locust/analysis_template.md``
  - standardized run result capture template.
- ``requirements-dev.txt``
  - optional developer dependency group containing Locust.
- ``docker-compose.metrics-api.override.yml``
  - optional containerized Metrics API runner for local stack workflows.
- ``src/digital_twin/presentation/metrics_api_runner.py``
  - minimal local runtime entrypoint to expose API on configurable host/port.

Documentation Updated
---------------------

- New engineering guide:
  ``docs/engineering/local_load_testing_locust.rst``.
- Engineering toctree inclusion:
  ``docs/engineering/index.rst``.
- Performance budget placeholders:
  ``docs/engineering/performance_budget.rst``.
- Architecture timeline entry:
  ``docs/architecture/evolution_history.rst``.

How to Run Locally
------------------

1. Install dependencies:

   .. code-block:: bash

      pip install -r requirements-dev.txt

2. Start shared stack (optional for end-to-end context):

   .. code-block:: bash

      docker compose -f docker-compose.stack.yml up -d

3. Start Metrics API (choose one):

   .. code-block:: bash

      export PYTHONPATH=src
      python -m digital_twin.presentation.metrics_api_runner

   or

   .. code-block:: bash

      docker compose -f docker-compose.stack.yml -f docker-compose.metrics-api.override.yml up -d metrics-api

4. Execute Locust profiles (headless examples):

   .. code-block:: bash

      LOCUST_PROFILE=steady_state_cache_hit locust -f load_testing/locust/locustfile.py --host http://localhost:8000 --headless -u 50 -r 5 -t 5m
      LOCUST_PROFILE=burst_dashboard_refresh locust -f load_testing/locust/locustfile.py --host http://localhost:8000 --headless -u 80 -r 20 -t 3m
      LOCUST_PROFILE=refresh_pressure REFRESH_TEST_MODE=1 REFRESH_TTL_SECONDS=0.25 locust -f load_testing/locust/locustfile.py --host http://localhost:8000 --headless -u 40 -r 5 -t 5m
      LOCUST_PROFILE=mixed_observability locust -f load_testing/locust/locustfile.py --host http://localhost:8000 --headless -u 60 -r 10 -t 5m

Profiles Description
--------------------

- ``steady_state_cache_hit``
  - high weight on ``/metrics`` with low incidental endpoint traffic.
- ``burst_dashboard_refresh``
  - burst-heavy repeated ``/metrics`` + dashboard companion endpoint calls.
- ``refresh_pressure``
  - periodic TTL-aligned waits to increase cache refresh probability safely.
- ``mixed_observability``
  - broad endpoint mixture with configurable per-endpoint weights.

Acceptance Gate Placeholders
----------------------------

- ``/metrics`` p95/p99 latency thresholds: TBD.
- ``/metrics/top`` p95/p99 latency thresholds: TBD.
- Refresh-spike max latency threshold: TBD.
- Error-rate SLO: TBD.
- Minimum sustained RPS threshold: TBD.

Determinism Safety Statement
----------------------------

The Phase 9E suite is observability-only. It sends read-only HTTP requests to
Metrics API endpoints and does not alter domain transition semantics, replay
ordering, or ingestion contracts.

Known Limitations
-----------------

- No CI-executed Locust load campaign is added in this phase.
- Final SLO values remain placeholders pending local baseline measurements.
- Refresh forcing relies on TTL timing (no dedicated refresh query parameter).
