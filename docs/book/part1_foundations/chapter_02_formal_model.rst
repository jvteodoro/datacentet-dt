Chapter 2 — Formal Model of the Digital Twin
=============================================

1. Conceptual Introduction
--------------------------

Problem Context
~~~~~~~~~~~~~~~

The formal model defines the semantic boundary of the Digital Twin: what states
are valid, what events are admissible, and how transitions become durable truth.
Without this boundary, replay guarantees and hyperscale ingestion behavior become
implementation accidents instead of architectural properties.

Conceptual Tension
~~~~~~~~~~~~~~~~~~

The current system must be both:

- strict enough to preserve deterministic replay and idempotent persistence;
- flexible enough to accept events from HTTP and Kafka ingress paths.

Abstraction Introduced
~~~~~~~~~~~~~~~~~~~~~~

The canonical abstraction remains:

.. math::

   \mathrm{System} = (X, E, H, V, \mathcal{I}, \mathcal{O})

where :math:`X` is state space, :math:`E` is normalized event space,
:math:`H` is transition, :math:`V` is validation, :math:`\mathcal{I}` is
inference, and :math:`\mathcal{O}` is optimization.

Formal Definition
~~~~~~~~~~~~~~~~~

At logical step :math:`k`, the operational chain is:

.. math::

   m_k \xrightarrow{N} e_k \xrightarrow{\mathrm{step}} x_{k+1}

where :math:`m_k` is transport message, :math:`N` is canonical normalizer,
:math:`e_k \in E` is normalized event, and :math:`\mathrm{step}` is the total
state update relation defined in Section 2.

Implementation Strategy
~~~~~~~~~~~~~~~~~~~~~~~

The implementation wires this abstraction through ``DataCenterTwin``:
normalization before transition, validation before commit, event-store append,
then state publication. See :doc:`../../engineering/determinism_and_replay` and
:doc:`../../engineering/real_db_protocol`.

Consequences
~~~~~~~~~~~~

This framing makes deterministic replay, idempotent duplicate handling, and
snapshot-based recovery analyzable as laws rather than incidental behavior.

2. Formal Framing
-----------------

Problem Context
~~~~~~~~~~~~~~~

The previous chapter introduced the tuple. This section hardens it into
operational laws that match the current code and protocols.

Conceptual Tension
~~~~~~~~~~~~~~~~~~

The architecture needs a total operational semantics even though runtime code
may throw exceptions during transition or validation. The model must describe
resulting state behavior independently from exception mechanics.

Abstraction Introduced
~~~~~~~~~~~~~~~~~~~~~~

Define a total step relation over current state :math:`x` and normalized event
:math:`e`.

Formal Definition
~~~~~~~~~~~~~~~~~

2.1 Determinism law (normalized sequence law)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let :math:`N` be the canonical normalizer, and :math:`\overline{E}_{1:n}` be the
ordered normalized event sequence:

.. math::

   \overline{E}_{1:n} = [N(m_1), N(m_2), \dots, N(m_n)]

For runs :math:`r_a, r_b`, determinism requires:

.. math::

   x_0^{(a)} = x_0^{(b)} \land \overline{E}_{1:n}^{(a)} = \overline{E}_{1:n}^{(b)}
   \land H, V \text{ deterministic}
   \Rightarrow x_n^{(a)} = x_n^{(b)}

with side-effect control condition: domain transition/validation semantics are
computed from :math:`(x,e)`; side-channel telemetry does not alter commit
outcomes.

2.2 Total step function with rollback semantics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let :math:`c = H(x,e)` be a transition candidate and
:math:`x' = \mathrm{state}(c)`.

.. math::

   \mathrm{step}(x,e) =
   \begin{cases}
   x' & \text{if } V(c)=\mathrm{true} \land \mathrm{append}(e,x')=\mathrm{APPENDED} \\
   x  & \text{if } V(c)=\mathrm{false} \;\;\text{(rollback)} \\
   x  & \text{if } \mathrm{append}(e,x')=\mathrm{ALREADY\_EXISTS}
   \end{cases}

This makes semantics total: for every :math:`(x,e)`, the post-state is defined.

2.3 Idempotency law
^^^^^^^^^^^^^^^^^^^

Per stream :math:`s`, idempotency key is :math:`(s, ingest\_id)`.

.. math::

   \mathrm{append}_s(e, ingest\_id)=\mathrm{ALREADY\_EXISTS}
   \Rightarrow
   \mathrm{step}_s(x,e)=x

State effect is null, but outcome observability is preserved via ingestion
status/metrics channels.

2.4 Replay equivalence theorem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let :math:`\mathcal{L}_{1:n}` be event-log truth in persisted order, and
:math:`x_m` be state reconstructed from snapshot prefix :math:`S_m`.

.. math::

   \mathrm{run}(x_0, \mathcal{L}_{1:n}) = x_n

.. math::

   \mathrm{run}(x_m, \mathcal{L}_{m+1:n}) = x_n

Hence snapshots are acceleration artifacts only; event log remains truth.

2.5 Multi-stream ordering contract
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For each stream :math:`s`, total order is guaranteed by per-stream append/replay
ordering and partition-key policy (:doc:`../../engineering/kafka_protocol`).
No global cross-stream order is assumed:

.. math::

   \forall s: \mathcal{L}^{(s)} \text{ totally ordered},
   \quad \nexists \text{ required global total order over } \bigcup_s \mathcal{L}^{(s)}

Cross-stream coordination, if required, must be encoded explicitly as domain
barrier/coordination events.

2.6 Transport non-interference principle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For transport messages :math:`m,m'` producing equal normalized domain event:

.. math::

   N(m)=N(m') \Rightarrow H(x,N(m)) = H(x,N(m'))

Transport metadata (partition, offset, HTTP path, source tags) is observational
side-channel data for forensics/metrics, not domain transition input.

Implementation Strategy
~~~~~~~~~~~~~~~~~~~~~~~

These laws are implemented with per-stream persistence, explicit rollback,
idempotent append semantics, and ordered replay reads.

Consequences
~~~~~~~~~~~~

The model captures current architecture limits and guarantees precisely: strong
per-stream replay safety, no global ordering claim, and explicit non-interference
boundary for transport metadata.

3. Code Walkthrough (Literate Programming)
------------------------------------------

Problem Context
~~~~~~~~~~~~~~~

The formal laws above are only valid if code paths enforce them in the same
order under live ingestion and replay.

Conceptual Tension
~~~~~~~~~~~~~~~~~~

Transition code mutates dynamic containers for performance. Deterministic
semantics must still hold via rollback and validation gates.

Abstraction Introduced
~~~~~~~~~~~~~~~~~~~~~~

``TransitionCandidate`` is the operational bridge between local mutable updates
and logically atomic step semantics.

Formal Definition
~~~~~~~~~~~~~~~~~

Rollback evidence from ``transition.py``:

.. code-block:: python

   @dataclass(frozen=True, slots=True)
   class TransitionCandidate:
       state: TwinState
       rollback_actions: tuple[Callable[[], None], ...] = field(default_factory=tuple)

       def rollback(self) -> None:
           for action in reversed(self.rollback_actions):
               action()

Pre-commit validation gate and rollback in ``twin.py``:

.. code-block:: python

   candidate = self._transition_fn(self._state, event)
   try:
       self._validator_fn(candidate)
   except Exception:
       if isinstance(candidate, TransitionCandidate):
           candidate.rollback()
       raise

Idempotent append in ``twin.py`` and ``event_store_pg.py``:

.. code-block:: python

   append_result = self._event_store.append(..., stream_id=..., ingest_id=event.event_id)
   if getattr(append_result, "value", append_result) == "ALREADY_EXISTS":
       if isinstance(candidate, TransitionCandidate):
           candidate.rollback()
       return

.. code-block:: python

   INSERT ...
   ON CONFLICT (stream_id, ingest_id) DO NOTHING

Ordered replay in ``event_store_pg.py``:

.. code-block:: sql

   SELECT version_counter, event_type, payload
   FROM event_log
   WHERE stream_id = %s
   ORDER BY seq ASC

Implementation Strategy
~~~~~~~~~~~~~~~~~~~~~~~

The core order is fixed: normalize -> transition -> validate -> append ->
publish state. Multi-stream ingestion composes this with one twin per stream
in ``MultiStreamCoordinator``.

Consequences
~~~~~~~~~~~~

The code supports total step semantics, per-stream idempotency, and replay
equivalence under ordered reads.

4. Invariants and Safety Guarantees
-----------------------------------

Problem Context
~~~~~~~~~~~~~~~

A formal model is only operationally useful when encoded as invariants that can
be audited during incidents and phase evolution.

Conceptual Tension
~~~~~~~~~~~~~~~~~~

Performance optimizations (local mutation, caching, partition scaling) can
silently erode semantics unless invariants remain explicit.

Abstraction Introduced
~~~~~~~~~~~~~~~~~~~~~~

The following invariants are treated as architecture constraints for the current
stack.

Formal Definition
~~~~~~~~~~~~~~~~~

- **I1 — Deterministic fold over normalized events:** identical initial state and
  identical ordered normalized events imply identical resulting state.
- **I2 — Validation gate pre-commit:** state publication requires successful
  validation of transition candidate.
- **I3 — Event-log primacy:** event log is truth; snapshots are acceleration for
  recovery only.
- **I4 — Idempotent ingestion key:** duplicate ``(stream_id, ingest_id)`` append
  yields no additional state effect.
- **I5 — Transport isolation:** transport metadata cannot alter :math:`H` or
  :math:`V` outcomes for equivalent normalized events.
- **I6 — Ordering scope contract:** total order is per stream; no global
  cross-stream ordering guarantee is assumed.

Implementation Strategy
~~~~~~~~~~~~~~~~~~~~~~~

These are enforced by event-store constraints, ordered replay queries,
normalizer boundaries, and coordinator stream isolation.

Consequences
~~~~~~~~~~~~

The system can scale stream cardinality while retaining deterministic replay at
stream scope.

5. Trade-offs
-------------

Problem Context
~~~~~~~~~~~~~~~

Every law has operational cost.

Conceptual Tension
~~~~~~~~~~~~~~~~~~

The project balances determinism guarantees against throughput and deployment
simplicity.

Abstraction Introduced
~~~~~~~~~~~~~~~~~~~~~~

Trade-offs are represented as explicit architecture decisions rather than hidden
defaults.

Formal Definition
~~~~~~~~~~~~~~~~~

- **Determinism vs flexibility:** strict normalizer and schema contracts reduce
  ambiguous ingestion behavior.
- **Replay guarantees vs write cost:** per-event idempotency/version checks add
  persistence overhead.
- **Per-stream isolation vs global reasoning convenience:** avoids unsafe global
  ordering assumptions but requires explicit cross-stream coordination events.
- **Snapshot frequency vs storage pressure:** faster recovery increases snapshot
  writes.

Implementation Strategy
~~~~~~~~~~~~~~~~~~~~~~~

Operational protocols in :doc:`../../engineering/kafka_protocol`,
:doc:`../../engineering/real_db_protocol`, and
:doc:`../../engineering/determinism_and_replay` keep these trade-offs explicit.

Consequences
~~~~~~~~~~~~

The current architecture prioritizes correctness and replayability over maximum
raw ingest throughput.

6. Limitations
--------------

Problem Context
~~~~~~~~~~~~~~~

The formal model must state what it does not guarantee yet.

Conceptual Tension
~~~~~~~~~~~~~~~~~~

Over-claiming guarantees creates operational risk under scale.

Abstraction Introduced
~~~~~~~~~~~~~~~~~~~~~~

Current limitations are documented as contract boundaries.

Formal Definition
~~~~~~~~~~~~~~~~~

- Cross-stream causality is **not** inferred from ingestion time; no global
  ordering theorem is claimed.
- p95/p99 SLO envelopes remain campaign-dependent placeholders until repeated
  load-testing campaigns are executed and baselined.
- Metrics API security hardening (authn/authz, rate limiting, perimeter
  controls) is deferred in this phase; current docs describe local/test focus.

Implementation Strategy
~~~~~~~~~~~~~~~~~~~~~~~

See :doc:`../../engineering/local_load_testing_locust`,
:doc:`../../engineering/local_load_testing_hyperscale_ingestion`, and
:doc:`../../engineering/observability_metrics_api`.

Consequences
~~~~~~~~~~~~

Operational decisions requiring global causality or production-grade metrics
security need additional architecture work beyond this chapter.

7. Evolution Path
-----------------

Problem Context
~~~~~~~~~~~~~~~

The formal model must remain stable as observability and scale tooling evolve.

Conceptual Tension
~~~~~~~~~~~~~~~~~~

Stack evolution should extend measurement power without changing domain truth
semantics.

Abstraction Introduced
~~~~~~~~~~~~~~~~~~~~~~

The next evolution path is side-channel observability expansion anchored to the
same deterministic core.

Formal Definition
~~~~~~~~~~~~~~~~~

- Continuity anchor: current architecture already includes persistence
  (Phase 8/8.1), streaming ingestion (9A/9C/9C.1), observability
  (9D/9D.1/9D.2), and load-testing foundations (9E/9E.1+).
- Operational trajectory: local-first CSV campaign analysis -> Prometheus/
  OpenTelemetry-oriented export path while preserving event-sourced replay truth.
- Performance closure strategy: repeated load campaigns + bounded-cardinality
  metrics refine p95/p99 envelopes and bottleneck attribution.

Implementation Strategy
~~~~~~~~~~~~~~~~~~~~~~~

See :doc:`../../engineering/observability_evolution_path_prometheus` and
:doc:`../../engineering/performance_budget`.

Consequences
~~~~~~~~~~~~

The model scales by adding measurement and deployment rigor around a stable
semantics core rather than altering transition laws.

Milestone note
--------------

Book Refactor Milestone: **Book v1.1 — Formalism Hardening + Multi-Stream
Semantics**.

Rationale partially inferred from code; limited historical explanation available.
