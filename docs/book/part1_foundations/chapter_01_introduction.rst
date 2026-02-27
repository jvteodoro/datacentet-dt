Chapter 1 — Introduction
========================

1. Conceptual Introduction
--------------------------

The Data Center Digital Twin is not a visualization artifact; it is a deterministic, event-sourced computational model of infrastructure behavior. The core architectural objective is to convert operational reality into a replayable state transition history so that analysis, optimization, and control can be performed with auditability.

Three constraints define the project from the beginning:

- **Determinism over convenience**: given the same initial state and event sequence, the twin must converge to the same state.
- **Event sourcing as truth**: the event log is the primary historical substrate; snapshots are acceleration artifacts.
- **Hyperscale by isolation**: streams, partitions, and bounded metrics preserve performance envelope under growth.

In formal terms, this project is organized around:

.. math::

   \mathrm{System} = (X, E, H, V, \mathcal{I}, \mathcal{O})

Where :math:`X` is state, :math:`E` is events, :math:`H` is deterministic transition, :math:`V` is validation, :math:`\mathcal{I}` is inference, and :math:`\mathcal{O}` is optimization.

This book exists to make that tuple operational for a new advanced engineer: from model, to code, to invariants, to production constraints.

2. Formal Framing
-----------------

At system scope, each ingestion step applies a pure logical pipeline:

.. math::

   e_k \xrightarrow{\text{normalize}} \tilde{e}_k \xrightarrow{H} x_{k+1} \xrightarrow{V} \{\mathrm{accept},\mathrm{reject}\}

Accepted transitions are persisted with monotonic versioning. Rejected transitions are rolled back and surfaced as explicit failures. This places correctness before throughput and enables replay safety.

The architectural contract can be expressed as:

.. math::

   (x_0, e_1, e_2, \dots, e_n) \Rightarrow x_n

with the determinism condition:

.. math::

   \forall i,j: (x_0^i = x_0^j) \land (E^i = E^j) \implies x_n^i = x_n^j

3. Code Walkthrough (Literate Programming)
------------------------------------------

The operational center is ``DataCenterTwin``. The class composes transition, validation, normalization, event persistence, and snapshot persistence into a single deterministic ingestion loop.

.. code-block:: python

   class DataCenterTwin:
       """Deterministic event-sourced core for the data center twin."""

       def ingest_event(self, event: DomainEvent) -> None:
           started_ns = perf_counter_ns()
           normalized_event = self._normalizer_fn(event)
           self._apply_normalized_event(normalized_event, persist_event=True)
           self._metrics.record_ingestion_latency(perf_counter_ns() - started_ns)

The architecture intentionally normalizes before transition. This ensures transport-specific variability does not leak into the domain operator :math:`H`.

The transition execution path includes rollback semantics for invalid candidates and idempotency behavior for duplicate appends:

.. code-block:: python

   candidate = self._transition_fn(self._state, event)
   self._validator_fn(candidate)
   append_result = self._event_store.append(...)
   if getattr(append_result, "value", append_result) == "ALREADY_EXISTS":
       candidate.rollback()
       return

This sequence encodes three non-obvious design choices:

- validation is mandatory before state publication;
- storage acknowledgement gates commit visibility;
- duplicate ingest IDs preserve idempotency and replay safety.

Recovery expresses event-sourcing semantics explicitly: load latest snapshot if available, then replay only events after snapshot version.

.. code-block:: python

   snapshot = self._snapshot_store.load_latest(stream_id=self._persistence_stream_id)
   if snapshot is not None:
       events = self._event_store.load_from(snapshot.version_counter, stream_id=self._persistence_stream_id)
   else:
       events = self._event_store.load_all(stream_id=self._persistence_stream_id)

4. Invariants and Safety Guarantees
-----------------------------------

The architecture relies on the following non-negotiable guarantees:

- **Replay invariance**: historical re-execution reproduces the same state trajectory.
- **Monotonic versioning**: applied events advance counters and ordering deterministically.
- **Idempotent ingestion**: duplicate ingress identifiers do not produce duplicate state effects.
- **Validation-before-commit**: invalid transitions must not become persistent truth.
- **Snapshot consistency**: snapshots summarize a prefix of the event history and never replace it as source of truth.

5. Trade-offs
-------------

- **Determinism vs flexibility**: stronger normalization and strict validation reduce schema drift tolerance.
- **Throughput vs auditability**: persistence checks add latency but preserve provable history.
- **Simplicity vs adaptability**: explicit transition and validation stages are verbose, but make behavior inspectable.
- **Memory vs speed**: snapshot intervals lower recovery time at storage overhead cost.

6. Limitations
--------------

This introductory layer does not solve:

- full stochastic uncertainty propagation;
- global multi-region ordering guarantees across independent streams;
- all autoscaling control policies;
- full long-horizon optimization proofs.

Those concerns are addressed in later architecture and operational chapters.

7. Evolution Path
-----------------

The system evolves by preserving the deterministic core while replacing infrastructure edges:

- local stores to hardened Postgres stores;
- local replay to partition-aligned Kafka replay;
- internal metrics snapshots to Prometheus-compatible export paths.

As load grows, the architecture scales by stream isolation, bounded observability cardinality, deterministic partition keying, and explicit rebalance safety protocols.
