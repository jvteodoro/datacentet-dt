Reporting Guidelines
====================

Policy Statement
----------------

No phase is considered complete without a corresponding agent report.

When Reports Are Mandatory
--------------------------

A phase report is mandatory whenever a roadmap phase reaches a gate decision,
including outcomes marked as passed, passed with warnings, or failed.

Reports are required for:

- Completion of any phase in :doc:`../engineering/implementation_roadmap`
- Any architectural change impacting :doc:`../architecture/system_blueprint`
- Any update affecting determinism or replay behavior in
  :doc:`../engineering/determinism_and_replay`
- Any performance-sensitive change governed by
  :doc:`../engineering/performance_budget`
- Any load-test execution under
  :doc:`../engineering/local_load_testing_protocol`

How Reports Are Written
-----------------------

Each report must be based on :doc:`phase_template` and must:

- Use precise technical language with reproducible claims.
- Distinguish measured results from assumptions.
- Record failed experiments and corrective actions.
- Preserve formal model notation:

  .. math::

     System = (X, E, H, V, \mathcal{I}, \mathcal{O})

Required Reproducibility Artifacts
----------------------------------

Each phase report must include references to artifacts required to reproduce
results:

- Commit hash (or exact repository snapshot identifier)
- Test commands and execution environment
- Input event streams or synthetic generation parameters
- Replay procedure and comparison method
- Configuration values used for load and performance runs

Required Metric Exports
-----------------------

Reports must include exported metrics and summary statistics aligned with
:doc:`../engineering/internal_metrics_architecture` and
:doc:`../engineering/performance_budget`, including where applicable:

- Throughput (events/s)
- Latency distributions (p50, p95, p99)
- Memory utilization
- Snapshot generation and retrieval cost
- Inference latency
- Optimization latency

Required Replay Verification
----------------------------

Every phase report must document replay verification and explicitly confirm
whether deterministic equivalence was preserved according to
:doc:`../engineering/determinism_and_replay`.

At minimum, include:

- Replay test command(s)
- Initial condition declaration
- Event sequence source
- Equality criteria for resulting state/snapshot
- Result status and any non-deterministic findings

How to Attach Locust Results
----------------------------

When load tests are executed, include:

- Locust scenario/profile name
- User count and spawn-rate configuration
- Duration and warm-up window
- Failure/timeout thresholds
- Aggregate and percentile latency tables
- Error distribution summary
- Export paths to raw Locust artifacts (CSV/JSON/HTML)

Locust results must be mapped to acceptance criteria from
:doc:`../engineering/local_load_testing_protocol`.

Naming Conventions
------------------

Phase report files must follow:

- ``docs/agent_report/phases/phase_X_report.rst``

Where ``X`` is the roadmap phase number (for example,
``phase_4_report.rst``).

Use section headings from :doc:`phase_template` without removal.
Additional subsections may be added for phase-specific detail.

Versioning Expectations
-----------------------

- Reports are version-controlled artifacts and must be committed with phase
  implementation evidence.
- Report updates after phase closure must append a clear revision note.
- Historical claims must remain auditable; avoid destructive rewrites that
  remove prior findings.
- If a gate decision changes, the report must retain prior decision context and
  document rationale for reclassification.
