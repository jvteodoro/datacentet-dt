Phase Report Template
=====================

Use this template for every phase report stored under
``docs/agent_report/phases/phase_X_report.rst``.

1. Phase Overview
-----------------

- **Phase number:**
- **Date:**
- **Commit reference (if available):**
- **Related roadmap section:** :doc:`../engineering/implementation_roadmap`

2. Architectural Scope
----------------------

- **Components introduced:**
- **Documents modified:**
- **Contracts affected:**
- **Data structures introduced:**

Reference architecture baseline: :doc:`../architecture/system_blueprint`.

3. Formal Model Impact
----------------------

- **Impact on** :math:`(X, E, H, V, \mathcal{I}, \mathcal{O})`:
- **State extensions (if any):**
- **Invariant extensions (if any):**

4. Determinism Verification
---------------------------

- **Replay tests executed:**
- **Results:**
- **Edge cases observed:**

Determinism claims must align with :doc:`../engineering/determinism_and_replay`.

5. Performance Validation
-------------------------

- **Throughput:**
- **p95 / p99 latency:**
- **Memory usage:**
- **Snapshot cost:**
- **Inference latency (if applicable):**
- **Optimization latency (if applicable):**

Performance acceptance must reference :doc:`../engineering/performance_budget`.

6. Load Testing Results
-----------------------

- **Load profile used:**
- **Duration:**
- **Failure conditions observed:**
- **Replay validation result:**

Use protocol alignment with :doc:`../engineering/local_load_testing_protocol`.

7. Contract Validation
----------------------

- **Invariants tested:**
- **Violations found:**
- **Resolution steps:**

8. Failure Propagation Observations
-----------------------------------

- **H failures:**
- **V failures:**
- **Inference failures:**
- **Optimization failures:**
- **Recovery behavior:**

9. Architectural Trade-offs
---------------------------

- **Performance vs clarity:**
- **Memory vs speed:**
- **Determinism safeguards:**
- **Simplifications made:**

10. Known Limitations
---------------------

- **Technical debt introduced:**
- **Performance ceilings:**
- **Unresolved risks:**

11. Phase Gate Decision
-----------------------

- **Passed**
- **Passed with warnings**
- **Failed (requires revision)**

12. Next Phase Preparation
--------------------------

- **Dependencies satisfied:**
- **Risks for next phase:**
- **Refactoring required before next phase:**

Required Cross-References
-------------------------

Each completed report must explicitly align conclusions with:

- :doc:`../architecture/system_blueprint`
- :doc:`../engineering/performance_budget`
- :doc:`../engineering/implementation_roadmap`
- :doc:`../engineering/local_load_testing_protocol`
- :doc:`../engineering/internal_metrics_architecture`
- :doc:`../engineering/determinism_and_replay`
