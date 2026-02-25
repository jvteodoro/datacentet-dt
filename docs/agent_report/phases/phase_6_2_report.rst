Phase 6.2 Report — EKF Comparative Validation
==============================================

1. Phase Overview
-----------------

- **Phase number:** 6.2
- **Date:** 2026-02-25
- **Commit reference (if available):** ``f9d360d``
- **Related roadmap section:** :doc:`../../engineering/implementation_roadmap`

2. Architectural Scope
----------------------

- **Components introduced:** ``EKFStrategy`` in ``src/digital_twin/inference/strategies/ekf.py`` with covariance-carrying 2D nonlinear estimation.
- **Documents modified:** ``docs/architecture/inference_architecture.rst`` and ``docs/architecture/evolution_history.rst``.
- **Contracts affected:** strict timestamp progression at inference boundary, covariance PSD preservation, finite-value enforcement, replay equivalence under ``LIVE``/``REPLAY``.
- **Data structures introduced:** no extension to physical domain state ``X``; epistemic state remains strategy-local.

Reference architecture baseline: :doc:`../../architecture/system_blueprint`.

3. Formal Model Impact
----------------------

- **Impact on** :math:`(X, E, H, V, \mathcal{I}, \mathcal{O})`: extends ``\mathcal{I}`` from moving-average-only (6/6.1) to covariance-aware nonlinear filtering (6.2) while preserving isolation from ``X``.
- **State extensions (if any):** none in domain state ``X``; EKF latent mean/covariance are internal inference strategy state.
- **Invariant extensions (if any):** explicit PSD-stable covariance evolution using Joseph form + symmetrization + deterministic inversion jitter.

4. Comparative Analysis (Phase 6.1 vs 6.2)
-------------------------------------------

+-----------------------------------+----------------------------------------------+----------------------------------------------------+
| Dimension                         | Phase 6.1                                     | Phase 6.2                                          |
+===================================+==============================================+====================================================+
| Estimator                         | Moving average                                | 2D EKF with nonlinear observation                  |
+-----------------------------------+----------------------------------------------+----------------------------------------------------+
| Latent epistemic state            | Running means only                            | Mean + 2x2 covariance (log-space)                  |
+-----------------------------------+----------------------------------------------+----------------------------------------------------+
| Observation model                 | Linear/direct aggregates                      | :math:`h(x)=[\exp(x_1),\exp(x_2)]^T`             |
+-----------------------------------+----------------------------------------------+----------------------------------------------------+
| Uncertainty propagation           | Not represented                               | Joseph-form covariance update                       |
+-----------------------------------+----------------------------------------------+----------------------------------------------------+
| Determinism mode behavior         | ``LIVE``/``REPLAY``/``DISABLED`` semantics   | Same semantics preserved                            |
+-----------------------------------+----------------------------------------------+----------------------------------------------------+
| Hyperscale extraction policy      | Aggregate-only active metrics                 | Aggregate-only active metrics (same constraint)     |
+-----------------------------------+----------------------------------------------+----------------------------------------------------+
| Timestamp policy                  | Canonical source defined in 6.1              | Strictly increasing validation enforced at runtime  |
+-----------------------------------+----------------------------------------------+----------------------------------------------------+

Key comparative conclusions:

- 6.2 adds scientifically meaningful uncertainty tracking without introducing domain mutation paths.
- Complexity remains bounded to O(1)/O(active metrics) because only aggregate snapshot fields are consumed.
- Replay determinism posture remains equivalent to 6.1, now including covariance trajectory equivalence.

5. Determinism Verification
---------------------------

- **Replay tests executed:**

  - ``PYTHONPATH=src pytest -q tests/inference/test_ekf_replay_equivalence.py``
  - ``PYTHONPATH=src pytest -q tests/inference/test_ekf_determinism.py``
  - ``PYTHONPATH=src pytest -q tests/inference/test_replay_epistemic_determinism.py``

- **Results:** identical parameter outputs for identical snapshot streams; replay output equals live output for EKF path.
- **Edge cases observed:** initialization step now yields canonical timestamp output, with updates occurring on subsequent snapshots.

Determinism claims must align with :doc:`../../engineering/determinism_and_replay`.

6. Performance Validation
-------------------------

- **Throughput:** not benchmarked in this phase report.
- **p95 / p99 latency:** not benchmarked in this environment.
- **Memory usage:** O(1) estimator memory (fixed-size 2D mean + 2x2 covariance + constants).
- **Snapshot cost:** unchanged; inference still reads immutable snapshots only.
- **Inference latency (if applicable):** O(1) deterministic 2x2 algebra; no global scans.
- **Optimization latency (if applicable):** not applicable in this phase.

Performance acceptance must reference :doc:`../../engineering/performance_budget`.

7. Load Testing Results
-----------------------

- **Load profile used:** not executed.
- **Duration:** not executed.
- **Failure conditions observed:** not executed.
- **Replay validation result:** passed in dedicated replay equivalence tests.

Use protocol alignment with :doc:`../../engineering/local_load_testing_protocol`.

8. Contract Validation
----------------------

- **Invariants tested:** finite parameter values, covariance symmetry/PSD, strict timestamp increase, aggregate-only extraction (no full array iteration), deterministic mode equivalence.
- **Violations found:** no violations in final validated run.
- **Resolution steps:** ensured engine initialization/update sequencing is compatible with strict timestamp contract.

9. Failure Propagation Observations
-----------------------------------

- **H failures:** unchanged.
- **V failures:** unchanged.
- **Inference failures:** fail-fast via parameter contract validation before persistence append.
- **Optimization failures:** not in scope.
- **Recovery behavior:** unchanged for physical state recovery; inference replay remains deterministic by mode semantics.

10. Architectural Trade-offs
----------------------------

- **Performance vs clarity:** manual deterministic 2x2 algebra improves control and predictability at minor implementation complexity cost.
- **Memory vs speed:** fixed small-state EKF preserves bounded memory and low computational overhead.
- **Determinism safeguards:** sorted strategy orchestration, canonical timestamp source, deterministic jitter constant, Joseph form + symmetrization.
- **Simplifications made:** state transition model fixed as random walk; covariance exported in latent log-space.

11. Known Limitations
---------------------

- **Technical debt introduced:** broader estimator benchmarking (UKF/particle) remains pending.
- **Performance ceilings:** no measured high-scale latency distribution for inference path in this report.
- **Unresolved risks:** future higher-dimensional estimators must preserve aggregate-only extraction and deterministic arithmetic ordering.

12. Phase Gate Decision
-----------------------

- **Passed with warnings**

Warnings:

- Repository-wide benchmark/load profile not executed in this runtime.

13. Next Phase Preparation
--------------------------

- **Dependencies satisfied:** covariance-carrying deterministic estimator now integrated in inference architecture.
- **Risks for next phase:** richer estimators may increase sensitivity to numeric conditioning and serialization format decisions.
- **Refactoring required before next phase:** add inference metrics export (latency and covariance diagnostics) aligned with internal metrics architecture.

Required Cross-References
-------------------------

This report aligns conclusions with:

- :doc:`../../architecture/system_blueprint`
- :doc:`../../architecture/inference_architecture`
- :doc:`../../engineering/performance_budget`
- :doc:`../../engineering/implementation_roadmap`
- :doc:`../../engineering/local_load_testing_protocol`
- :doc:`../../engineering/internal_metrics_architecture`
- :doc:`../../engineering/determinism_and_replay`
