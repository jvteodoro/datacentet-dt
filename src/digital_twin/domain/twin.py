from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Union
from time import perf_counter_ns

from .event import DomainEvent, normalize_event
from .metrics import MetricsCollector
from .snapshot import TwinSnapshot, build_snapshot
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
    ) -> None:
        self._state = _build_initial_state()
        self._snapshot = build_snapshot(self._state)
        self._event_log: list[DomainEvent] = []
        self._metrics = MetricsCollector()
        self._transition_fn = transition_fn
        self._validator_fn = validator_fn
        self._normalizer_fn = normalizer_fn

    @property
    def event_log(self) -> tuple[DomainEvent, ...]:
        return tuple(self._event_log)

    @property
    def state(self) -> TwinState:
        # Logical immutability boundary: expose copied dynamic containers only.
        return TwinState(
            version_counter=self._state.version_counter,
            event_counter=self._state.event_counter,
            topology=self._state.topology,
            compute_topology=self._state.compute_topology,
            link_backlog=list(self._state.link_backlog),
            active_flows=dict(self._state.active_flows),
            cpu_usage=list(self._state.cpu_usage),
            memory_usage=list(self._state.memory_usage),
            active_workloads=dict(self._state.active_workloads),
        )

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    def ingest_event(self, event: DomainEvent) -> None:
        started_ns = perf_counter_ns()

        # 1) normalize(event)
        normalized_event = self._normalizer_fn(event)

        # 2) X_candidate = H(X_current, event)
        candidate = self._transition_fn(self._state, normalized_event)

        # 3) V(X_candidate) -> valid or error
        try:
            self._validator_fn(candidate)
        except Exception:
            if isinstance(candidate, TransitionCandidate):
                candidate.rollback()
            raise

        # 4) If valid: commit state -> append event log -> update snapshot -> update metrics
        self._state = candidate.state if isinstance(candidate, TransitionCandidate) else candidate
        self._event_log.append(normalized_event)
        self._snapshot = build_snapshot(self._state)
        self._metrics.record_ingestion_latency(perf_counter_ns() - started_ns)

    def get_snapshot(self) -> TwinSnapshot:
        return self._snapshot

    def replay(self, event_sequence: Iterable[DomainEvent]) -> None:
        self._state = _build_initial_state()
        self._snapshot = build_snapshot(self._state)
        self._event_log = []
        self._metrics = MetricsCollector()

        for event in event_sequence:
            self.ingest_event(event)


def _build_initial_state() -> TwinState:
    return TwinState()
