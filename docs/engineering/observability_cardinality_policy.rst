Observability Cardinality & Cost Policy
=======================================

Scope
-----

This policy defines hard constraints for metrics cardinality, payload size, and
request-path cost for the read-only observability API.

Always-on Metrics Rules
-----------------------

Always-on metrics in ``/metrics`` must be aggregate-only and bounded:

- counters, sums, maxima, and active-entity counts are allowed;
- fixed-shape payloads are required;
- always-on output must not include unbounded entity lists.

Forbidden Dimensions
--------------------

The always-on snapshot must not expose high-cardinality dimensions:

- ``flow_id``
- ``workload_id``
- full per-entity dumps (flows/workloads/links/servers)

Bounded Top-K Rules
-------------------

Granular insights are allowed only through bounded Top-K structures:

- default limit: ``OBS_TOPK_DEFAULT = 20``;
- hard maximum: ``OBS_TOPK_HARD_MAX = 100``;
- API-level limit requests are clamped to hard maximum;
- stable ordering: ``(value DESC, id ASC)``.

Histogram Discipline
--------------------

Histograms must use fixed, deterministic bins configured in code:

- ``OBS_HIST_BINS_BACKLOG``
- ``OBS_HIST_BINS_CPU``
- ``OBS_HIST_BINS_MEM``

Dynamic bin derivation from runtime data is forbidden.

Deterministic Ordering Requirements
-----------------------------------

All API payloads must be deterministic-safe:

- JSON key ordering is sorted;
- Top-K entries use deterministic tie-breaking;
- histogram bin edges are stable and counts align to fixed intervals.

Hyperscale Constraints
----------------------

- ``/metrics`` cache-hit path is O(1);
- request path does not execute unbounded scans;
- computation is performed at refresh time only and bounded by snapshot arrays;
- no mutation of domain state, event log, inference state, or optimization state.

Cache Interaction Policy
------------------------

- read endpoints are cache-backed;
- cache hits do not trigger refresh;
- refresh failures return last snapshot and increment observability error counter;
- staleness is TTL-bounded (``METRICS_CACHE_TTL_MS``).
