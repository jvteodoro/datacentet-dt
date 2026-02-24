Codex Guidelines
================

1. Purpose
----------

This document defines mandatory guidelines for automated code generation and future contributions.

The Data Center Digital Twin is not a generic software project.

It is a mathematically defined system:

.. math::

   DigitalTwin = (X, E, H, V)

Where:

- X = state space
- E = event space
- H = deterministic transition operator
- V = validation operator

All future modifications must preserve this structure.

---

2. Non-Negotiable Principles
----------------------------

The following principles must never be violated:

1. Domain purity
2. Determinism
3. Causal ordering
4. Invariant preservation
5. Infrastructure isolation

If a change violates any of these, it must be rejected.

---

3. Domain Purity Rule
---------------------

The domain layer must:

- Not import infrastructure modules
- Not access system clock
- Not use threads
- Not use async
- Not use external frameworks
- Not use I/O

All state transitions must be pure and deterministic.

---

4. Determinism Rule
-------------------

All transitions must be deterministic.

Forbidden inside domain:

- Random number generation (unless explicitly seeded and controlled)
- Non-ordered iteration over sets or dicts that affects state
- Implicit time progression
- Hidden mutable globals

Replay must always produce identical state.

---

5. Event-Centric Evolution Rule
--------------------------------

All state evolution must occur through events.

No component may:

- Mutate state without going through event handling
- Bypass the InternalEventBus
- Modify state directly from infrastructure

The EventBus implements H.

Bypassing it breaks semantics.

---

6. Validation Rule
------------------

Every new subsystem must:

1. Define its invariants.
2. Extend validation operator V.
3. Provide contract tests.

No feature is complete without validation.

Validation must:

- Not mutate state
- Fail loudly
- Be deterministic

---

7. Extension Workflow
---------------------

When adding new functionality:

Step 1 — Define formal state variables.

Step 2 — Define transition equations.

Step 3 — Define conservation laws (if applicable).

Step 4 — Define physical limits.

Step 5 — Define temporal constraints.

Step 6 — Extend validation operator.

Step 7 — Write unit, integration, and replay tests.

Step 8 — Update documentation.

Do not start from infrastructure.

---

8. Floating Point Discipline
----------------------------

Because real numbers are used:

- Define explicit epsilon tolerance.
- Avoid unstable arithmetic sequences.
- Maintain consistent operation ordering.

Never hide numerical drift.

---

9. Snapshot Integrity
---------------------

Snapshots must:

- Be immutable.
- Reflect domain state exactly.
- Not expose internal mutable objects.

Snapshots are part of scientific auditing.

---

10. Infrastructure Boundaries
-----------------------------

Infrastructure may:

- Deliver events.
- Persist snapshots.
- Visualize state.

Infrastructure may not:

- Modify domain state.
- Skip validation.
- Alter event ordering.

Infrastructure is replaceable.
Domain is not.

---

11. Adding Concurrency (Future)
-------------------------------

Concurrency is forbidden in MVP.

If introduced in future:

- Formal concurrency model must be defined.
- Determinism must be preserved or explicitly relaxed with formal reasoning.
- Replay semantics must be updated.

Concurrency cannot be introduced casually.

---

12. Scientific Responsibility
-----------------------------

The Digital Twin is a scientific instrument.

Code generation must respect:

- Physical realism
- Mathematical consistency
- Reproducibility
- Auditability

If an implementation simplifies a law,
it must document the approximation explicitly.

---

13. Anti-Patterns (Strictly Forbidden)
---------------------------------------

- Direct state mutation bypassing event handling
- Silent correction of invalid states
- Hidden side effects
- Catch-and-ignore validation errors
- Infrastructure imports inside domain
- Implicit default timestamps
- Auto-generated random IDs without determinism awareness

---

14. When in Doubt
-----------------

If uncertain about an extension:

1. Revisit system_model.rst
2. Revisit event_dynamics.rst
3. Revisit contracts.rst
4. Revisit validation_operator.rst

Theoretical consistency precedes implementation convenience.

---

15. Summary
-----------

The Digital Twin must remain:

- Deterministic
- Physically grounded
- Architecturally isolated
- Normatively validated
- Scientifically reproducible

Any generated code must preserve:

.. math::

   (X, E, H, V)

This document protects the long-term integrity of the system.