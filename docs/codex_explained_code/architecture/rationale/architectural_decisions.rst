Architectural Decisions
=======================

Decision: Deterministic ingest pipeline
---------------------------------------
Context: Replay correctness and canonical ordering were early explicit goals.
Problem: Without fixed ordering, validation and persistence can diverge across runs.
Alternatives Considered: direct commit-before-validate; asynchronous validation.
Chosen Approach: normalize -> transition -> validate -> commit ordering in ``DataCenterTwin``.
Rationale: Supported by deterministic replay tests and phase reports.
Consequences: Rejected events leave no committed side effects.
Related Commits: ``c414d9f``, ``5b270d4``.
Related Agent Reports: ``phase_1_report.rst``.

Decision: TransitionCandidate metadata carrier
----------------------------------------------
Context: Validation needed locality without polluting committed state.
Problem: Modified-link/flow metadata was needed by validator but not by persisted state.
Alternatives Considered: store modified sets in ``TwinState``; global validator scan.
Chosen Approach: introduce ``TransitionCandidate`` with modified indices and rollback actions.
Rationale: Explicitly documented in phase 2 / 2.1 reports.
Consequences: Cleaner state model and localized validation.
Related Commits: ``b2c90ee``, ``993d1fb``.
Related Agent Reports: ``phase_2_report.rst``, ``phase_2_1_report.rst``.

Decision: Logical immutability with rollback
--------------------------------------------
Context: Phase 2.2 sought lower copy costs while retaining deterministic safety.
Problem: Full-copy strategy was correct but expensive for high-frequency flow events.
Alternatives Considered: full immutable copies each transition; unrestricted in-place mutation.
Chosen Approach: internal in-place mutations plus explicit rollback on validation failure.
Rationale: Rationale partially inferred from commit message; limited historical explanation available.
Consequences: Better update locality, higher rollback complexity burden.
Related Commits: ``993d1fb``.
Related Agent Reports: ``phase_2_2_report.rst``.
