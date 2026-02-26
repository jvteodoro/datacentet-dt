Local Load Testing: HTTP Ingestion Gateway
==========================================

This document defines a reproducible local workflow for ingestion-path load testing
using the Phase 9E.1 HTTP gateway and deterministic Locust traffic generation.

Scope
-----

The workflow exercises the canonical domain path:

``normalize -> H -> V -> commit -> persist -> snapshot``

through an HTTP boundary, while preserving per-stream event ordering and idempotent
``ingest_id`` semantics.

Prerequisites
-------------

1. Local Python environment with project dependencies installed.
2. PostgreSQL configured for persistence adapters if persistence timing is required.
3. Optional Locust installation for traffic generation.

Runbook
-------

1. Start ingestion gateway:

   .. code-block:: bash

      HOST=0.0.0.0 PORT=8091 REQUIRE_INGEST_ID=1 python -m digital_twin.presentation.ingestion_http_runner

2. Start Locust ingestion suite:

   .. code-block:: bash

      cp load_testing/locust_ingest/config.example.env .env
      locust -f load_testing/locust_ingest/locustfile.py --host http://127.0.0.1:8091

3. Choose profile with ``LOCUST_INGEST_PROFILE``:

   - ``steady_poisson_users``
   - ``burst_pareto_users``
   - ``multi_stream_scale``
   - ``tick_heavy_infra``
   - ``mixed_with_flows``

4. Set deterministic seed:

   .. code-block:: bash

      export LOCUST_SEED=42

5. Collect gateway-side health metrics:

   .. code-block:: bash

      curl -s http://127.0.0.1:8091/health/metrics

Expected outcomes
-----------------

- HTTP response body reports ``APPLIED``, ``DUPLICATE``, ``DLQ``, or ``VERSION_CONFLICT``.
- Validation failures return HTTP 400 and ``dlq_reason``.
- Version conflicts return HTTP 409 with conflict details.
- Batch ingestion uses deterministic ordering by
  ``(source_time_utc, ingest_id)`` for replay-stable handling.

Determinism notes
-----------------

- Locust suite generates client-side ``ingest_id`` for replay comparability.
- Server-side ``ingest_id`` generation is disabled by default for this workflow
  (``REQUIRE_INGEST_ID=1``).
- Ordering policy and idempotency requirements align with determinism and replay
  guidance in :doc:`determinism_and_replay`.

Phase 9E.2 additions
--------------------

Use ``load_testing/campaigns/run_http_campaign.sh`` as the source-of-truth runner.
It creates ``load_testing/runs/<run_id>/`` with ``manifest.yml``, Locust CSV files,
``resource_usage.csv``, free-form ``notes.md``, and derived analysis markdown.

Scenario matrix for bottleneck attribution:

- domain-only: in-memory event/snapshot stores.
- db-backed events only: EventStorePG enabled, snapshots disabled.
- db + snapshots: EventStorePG and SnapshotStorePG enabled.

Run each scenario with the same ``SEED``, profile, users, and duration to preserve
logical workload equivalence.
