from __future__ import annotations

from collections.abc import Callable, Iterable
from time import perf_counter_ns

from .event import DomainEvent, normalize_event
from .metrics import MetricsCollector
from .snapshot import TwinSnapshot, build_snapshot
from .state import TwinState
from .transition import apply_transition
from .validation import validate_state


class DataCenterTwin:
    """Deterministic event-sourced core for Phase 1."""

    def __init__(
        self,
        *,
        transition_fn: Callable[[TwinState, DomainEvent], TwinState] = apply_transition,
        validator_fn: Callable[[TwinState], None] = validate_state,
        normalizer_fn: Callable[[DomainEvent], DomainEvent] = normalize_event,
    ) -> None:
        self._initial_state = TwinState()
        self._state = self._initial_state
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
        return self._state

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    def ingest_event(self, event: DomainEvent) -> None:
        started_ns = perf_counter_ns()

        # 1) normalize(event)
        normalized_event = self._normalizer_fn(event)

        # 2) X_candidate = H(X_current, event)
        candidate_state = self._transition_fn(self._state, normalized_event)

        # 3) V(X_candidate) -> valid or error
        self._validator_fn(candidate_state)

        # 4) If valid: commit state -> append event log -> update snapshot -> update metrics
        self._state = candidate_state
        self._event_log.append(normalized_event)
        self._snapshot = build_snapshot(self._state)
        self._metrics.record_ingestion_latency(perf_counter_ns() - started_ns)

    def get_snapshot(self) -> TwinSnapshot:
        return self._snapshot

    def replay(self, event_sequence: Iterable[DomainEvent]) -> None:
        self._state = self._initial_state
        self._snapshot = build_snapshot(self._state)
        self._event_log = []
        self._metrics = MetricsCollector()

        for event in event_sequence:
            self.ingest_event(event)
