from __future__ import annotations

from collections.abc import Callable, Iterable
from time import perf_counter_ns
from typing import Union

from .event import DomainEvent, normalize_event
from .metrics import MetricsCollector
from .snapshot import TwinSnapshot, build_snapshot, state_from_snapshot
from .state import TwinState
from .transition import TransitionCandidate, apply_transition
from .validation import validate_state


class DataCenterTwin:
    """Deterministic event-sourced core for the data center twin."""

    def __init__(
        self,
        *,
        transition_fn: Callable[[TwinState, DomainEvent], Union[TwinState, TransitionCandidate]] = apply_transition,
        validator_fn: Callable[[Union[TwinState, TransitionCandidate]], None] = validate_state,
        normalizer_fn: Callable[[DomainEvent], DomainEvent] = normalize_event,
        event_store: object | None = None,
        snapshot_store: object | None = None,
        snapshot_interval: int = 1000,
        persistence_stream_id: str = "default",
    ) -> None:
        if snapshot_interval <= 0:
            raise ValueError("snapshot_interval must be > 0")

        self._state = _build_initial_state()
        self._snapshot = build_snapshot(self._state)
        self._metrics = MetricsCollector()
        self._transition_fn = transition_fn
        self._validator_fn = validator_fn
        self._normalizer_fn = normalizer_fn
        self._event_store = event_store if event_store is not None else _LocalEventStore()
        self._snapshot_store = snapshot_store if snapshot_store is not None else _LocalSnapshotStore()
        self._snapshot_interval = snapshot_interval
        self._persistence_stream_id = persistence_stream_id

    @property
    def event_log(self) -> tuple[DomainEvent, ...]:
        return tuple(self._event_store.load_all())

    @property
    def state(self) -> TwinState:
        return TwinState(
            version_counter=self._state.version_counter,
            event_counter=self._state.event_counter,
            topology=self._state.topology,
            compute_topology=self._state.compute_topology,
            link_backlog=list(self._state.link_backlog),
            active_flows=dict(self._state.active_flows),
            cpu_usage=list(self._state.cpu_usage),
            memory_usage=list(self._state.memory_usage),
            server_workload_count=list(self._state.server_workload_count),
            active_workloads=dict(self._state.active_workloads),
            active_link_indices=set(self._state.active_link_indices),
            active_server_indices=set(self._state.active_server_indices),
        )

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    def ingest_event(self, event: DomainEvent) -> None:
        started_ns = perf_counter_ns()
        normalized_event = self._normalizer_fn(event)
        self._apply_normalized_event(normalized_event, persist_event=True)
        self._metrics.record_ingestion_latency(perf_counter_ns() - started_ns)

    def _apply_normalized_event(self, event: DomainEvent, *, persist_event: bool) -> None:
        candidate = self._transition_fn(self._state, event)

        try:
            self._validator_fn(candidate)
        except Exception:
            if isinstance(candidate, TransitionCandidate):
                candidate.rollback()
            raise

        self._state = candidate.state if isinstance(candidate, TransitionCandidate) else candidate
        if persist_event:
            self._event_store.append(
                event,
                stream_id=self._persistence_stream_id,
                version_counter=self._state.version_counter,
                event_type=event.type,
                payload=dict(event.payload),
                ingest_id=event.event_id,
            )
        self._snapshot = build_snapshot(self._state)
        if self._state.event_counter % self._snapshot_interval == 0:
            self._snapshot_store.save(
                self._snapshot,
                stream_id=self._persistence_stream_id,
                version_counter=self._snapshot.version_counter,
            )

    def get_snapshot(self) -> TwinSnapshot:
        return self._snapshot

    def replay(self, event_sequence: Iterable[DomainEvent]) -> None:
        self._state = _build_initial_state()
        self._snapshot = build_snapshot(self._state)
        self._metrics = MetricsCollector()

        for event in event_sequence:
            self.ingest_event(event)

    def recover(self) -> None:
        snapshot = self._snapshot_store.load_latest(stream_id=self._persistence_stream_id)
        self._metrics = MetricsCollector()

        if snapshot is not None:
            self._state = state_from_snapshot(snapshot)
            self._snapshot = snapshot
            events = self._event_store.load_from(snapshot.version_counter, stream_id=self._persistence_stream_id)
        else:
            self._state = _build_initial_state()
            self._snapshot = build_snapshot(self._state)
            events = self._event_store.load_all(stream_id=self._persistence_stream_id)

        for event in events:
            self._apply_normalized_event(event, persist_event=False)


def _build_initial_state() -> TwinState:
    return TwinState()


class _LocalEventStore:
    def __init__(self) -> None:
        self._events: list[tuple[int, DomainEvent]] = []

    def append(self, event: DomainEvent, **kwargs: object) -> None:
        version_counter = int(kwargs.get("version_counter", event.version))
        self._events.append((version_counter, event))

    def load_all(self, **_: object) -> tuple[DomainEvent, ...]:
        return tuple(event for _, event in self._events)

    def load_from(self, version: int, **_: object) -> tuple[DomainEvent, ...]:
        return tuple(event for version_counter, event in self._events if version_counter > version)


class _LocalSnapshotStore:
    def __init__(self) -> None:
        self._snapshot: TwinSnapshot | None = None

    def save(self, snapshot: TwinSnapshot, **_: object) -> None:
        self._snapshot = snapshot

    def load_latest(self, **_: object) -> TwinSnapshot | None:
        return self._snapshot
