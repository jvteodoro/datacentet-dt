Observability Metrics API
=========================

Purpose
-------

Phase 9D introduces a unified, read-only observability pipeline that exports
operational metrics as deterministic-safe side channels for dashboards.

Determinism-Safe Rule
---------------------

Metrics are observational only and must never:

- alter event ordering,
- alter transition/validation outcomes (:math:`H` / :math:`V`),
- alter persisted event-log truth,
- alter replayed domain state.

Metrics collection runs outside transition logic and is restricted to aggregate
counter/gauge/histogram snapshots.

LIVE vs REPLAY Semantics
------------------------

Runtime observability values may differ across ``LIVE`` and ``REPLAY`` modes due
wall-clock, process timing, runtime I/O, and external adapter behavior.

However, deterministic contract requirements remain:

- domain state must match for equivalent event sequences,
- persisted event ordering/content must match,
- replay output at domain boundary must remain equivalent.

Hyperscale Safety
-----------------

To preserve hyperscale characteristics, metrics exposure follows these rules:

- expose aggregate-only values,
- avoid scans over full topology/domain containers,
- keep collection complexity linear in number of exported metrics,
- avoid lock contention in ingestion path by using short lock windows and
  immutable snapshots from providers.

Dashboard API Contract
----------------------

Endpoints are read-only:

- ``GET /health`` -> ``{"status":"ok"}``
- ``GET /metrics`` -> unified ``MetricsSnapshot`` payload
- ``GET /metrics/schema`` -> metric descriptors (name/kind/unit/description/labels)
- ``GET /metrics/streams`` -> stream operations aggregates

Schema stability guidance:

- metric names are stable keys,
- kinds are one of ``counter``, ``gauge``, ``histogram``,
- units are explicit where applicable,
- labels are minimal and string-only,
- JSON payload keys are serialized in sorted order.

Security Note
-------------

Current phase intentionally leaves endpoints unauthenticated for local dashboard
integration and testing. Production deployments should add authn/authz,
rate-limiting, and network isolation.

Suggested Dashboard Visualizations
----------------------------------

- ingestion throughput and latency trend (domain counters + gauges),
- DB adapter latency envelope and error counters,
- active streams + eviction trends,
- ingestion outcome breakdown by status,
- optional Kafka lag indicator for operational backlog monitoring.


Refresh & Staleness Semantics
-----------------------------

To make ``/metrics`` predictable under hyperscale load, API serving uses a
cached ``MetricsSnapshot`` with explicit refresh semantics.

- default cache TTL: ``METRICS_CACHE_TTL_MS=200`` ms;
- refresh policy: TTL-driven with optional manual refresh trigger;
- request behavior: repeated calls inside TTL are served from cache;
- steady-state staleness guarantee: snapshot age is bounded by approximately
  ``ttl_ms`` (plus scheduling/network jitter).

Failure fallback behavior:

- if a refresh attempt fails and a previous snapshot exists, the API returns
  the last cached snapshot;
- an observability-side error counter metric is incremented
  (``observability.cache_refresh_errors_total``);
- this failure handling remains observational and does not affect domain
  ingestion, validation, persistence ordering, or replay semantics.


Expanded Coverage (Phase 9D.2)
------------------------------

The unified snapshot now includes three bounded blocks:

- ``metrics``: aggregate counters/gauges/histogram-style scalar aggregates;
- ``topk``: bounded granular rankings (deterministic ordering);
- ``histograms``: fixed-bin distributions.

Additional read-only endpoints:

- ``GET /metrics/top`` -> bounded Top-K payloads (optional ``?limit=`` clamped)
- ``GET /metrics/histograms`` -> fixed histogram definitions and counts

New insight providers:

- ``NetworkInsightProvider``
  - always-on: ``net.active_flows.count``, ``net.backlog.total``, ``net.backlog.max``
  - granular: ``top.links.by_backlog``, ``hist.net.backlog``
- ``ComputeInsightProvider``
  - always-on: ``compute.active_workloads.count``, ``compute.cpu_usage.total``,
    ``compute.cpu_usage.max``, ``compute.mem_usage.total``, ``compute.mem_usage.max``
  - granular: ``top.servers.by_cpu``, ``top.servers.by_mem``,
    ``hist.compute.cpu_usage``, ``hist.compute.mem_usage``

Cardinality and bounding policy is defined in
:doc:`observability_cardinality_policy`.
