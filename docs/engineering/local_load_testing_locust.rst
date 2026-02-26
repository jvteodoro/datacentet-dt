Local Load Testing with Locust (Phase 9E)
=========================================

Purpose and Scope
-----------------

This guide defines a repeatable, local-only load-testing workflow for the
read-only observability Metrics API.

Target endpoints:

- ``GET /health``
- ``GET /metrics``
- ``GET /metrics/schema``
- ``GET /metrics/streams``
- ``GET /metrics/top``
- ``GET /metrics/histograms``

Determinism safety constraints:

- load generation must not bypass ``DataCenterTwin.ingest_event``;
- Locust traffic in this phase is observability-only API reads;
- no mutation endpoint is introduced for load testing;
- results are operational side-channel measurements and must not be interpreted
  as domain-state changes.

Performance Budget Mapping
--------------------------

Phase 9E scenarios align with performance budget placeholders in
:doc:`performance_budget`:

- ``steady_state_cache_hit``
  - validates baseline ``/metrics`` p95/p99 and sustained RPS floor
  - validates low error-rate behavior under cache-hit dominant traffic
- ``burst_dashboard_refresh``
  - validates burst tolerance for dashboard-style repeated polling
  - checks p95/p99 for ``/metrics`` + ``/metrics/top`` under burst pressure
- ``refresh_pressure``
  - characterizes refresh-path latency spikes (max spike threshold)
  - compares cache-hit latency vs refresh-triggered latency
- ``mixed_observability``
  - validates realistic mixed endpoint distribution + aggregate error rate

Required metrics to report:

- requests/sec (RPS)
- error rate (%)
- latency p50/p95/p99 (at minimum for ``/metrics`` and ``/metrics/top``)
- payload size estimates (bytes) for key endpoints
- refresh spike characterization (max and distribution)

Install Dev Dependencies
------------------------

Use the dedicated optional developer requirements:

.. code-block:: bash

   pip install -r requirements-dev.txt

Start Local Stack (Postgres + Kafka)
------------------------------------

Bring up the shared infrastructure stack:

.. code-block:: bash

   docker compose -f docker-compose.stack.yml up -d

Stop it when done:

.. code-block:: bash

   docker compose -f docker-compose.stack.yml down

Start Metrics API
-----------------

Option A — local process (no container):

.. code-block:: bash

   export PYTHONPATH=src
   export METRICS_API_HOST=0.0.0.0
   export METRICS_API_PORT=8000
   export MODE=LIVE
   export NODE_ID=metrics-api-local
   export METRICS_CACHE_TTL_MS=200
   python -m digital_twin.presentation.metrics_api_runner

Option B — optional compose override (containerized API):

.. code-block:: bash

   docker compose \
     -f docker-compose.stack.yml \
     -f docker-compose.metrics-api.override.yml \
     up -d metrics-api

Run Locust Profiles
-------------------

Base setup:

.. code-block:: bash

   cp load_testing/locust/config.example.env load_testing/locust/.env
   set -a && source load_testing/locust/.env && set +a

Headless run (defaults from env file):

.. code-block:: bash

   locust -f load_testing/locust/locustfile.py \
     --host "$LOCUST_HOST" \
     --users "$LOCUST_USERS" \
     --spawn-rate "$LOCUST_SPAWN_RATE" \
     --run-time "$LOCUST_RUN_TIME" \
     --headless

Web UI run:

.. code-block:: bash

   locust -f load_testing/locust/locustfile.py --host "$LOCUST_HOST"

Per-profile commands:

.. code-block:: bash

   LOCUST_PROFILE=steady_state_cache_hit locust -f load_testing/locust/locustfile.py --host "$LOCUST_HOST" --headless -u 50 -r 5 -t 5m
   LOCUST_PROFILE=burst_dashboard_refresh locust -f load_testing/locust/locustfile.py --host "$LOCUST_HOST" --headless -u 80 -r 20 -t 3m
   LOCUST_PROFILE=refresh_pressure REFRESH_TEST_MODE=1 REFRESH_TTL_SECONDS=0.25 locust -f load_testing/locust/locustfile.py --host "$LOCUST_HOST" --headless -u 40 -r 5 -t 5m
   LOCUST_PROFILE=mixed_observability locust -f load_testing/locust/locustfile.py --host "$LOCUST_HOST" --headless -u 60 -r 10 -t 5m

Export CSV/HTML Results
-----------------------

.. code-block:: bash

   mkdir -p load_testing/locust/results
   locust -f load_testing/locust/locustfile.py \
     --host "$LOCUST_HOST" \
     --users "$LOCUST_USERS" \
     --spawn-rate "$LOCUST_SPAWN_RATE" \
     --run-time "$LOCUST_RUN_TIME" \
     --headless \
     --csv load_testing/locust/results/phase9e_run \
     --html load_testing/locust/results/phase9e_run.html

Use ``load_testing/locust/analysis_template.md`` to summarize findings.

Cache-Hit vs Refresh Interpretation
-----------------------------------

Current API behavior in this phase:

- no dedicated ``?refresh=1`` query parameter is exposed;
- refresh pressure is emulated safely using TTL-aligned pauses.

``refresh_pressure`` profile behavior:

- when ``REFRESH_TEST_MODE=1``, each user periodically sleeps for
  ``REFRESH_TTL_SECONDS + small_buffer`` after a request cycle;
- this increases cache-expiry probability and therefore refresh-path samples;
- no endpoint mutation or hidden write path is required.

If more refresh contrast is needed locally, reduce API cache TTL:

.. code-block:: bash

   export METRICS_CACHE_TTL_MS=50

Avoiding Misleading Results
---------------------------

- include a warm-up period before recording metrics;
- keep ``METRICS_CACHE_TTL_MS`` fixed for comparison runs;
- keep user/spawn/runtime fixed when comparing profiles;
- collect at least p50/p95/p99, RPS, and error rate per run;
- report host resource envelope (CPU/RAM) alongside Locust outputs;
- avoid mixing unrelated background workloads during benchmark runs.
