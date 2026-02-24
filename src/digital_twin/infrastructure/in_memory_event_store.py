from __future__ import annotations

from collections.abc import Iterable

from digital_twin.application.ports.event_store import EventStore
from digital_twin.domain.event import DomainEvent


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def append(self, event: DomainEvent) -> None:
        self._events.append(event)

    def load_all(self) -> Iterable[DomainEvent]:
        return tuple(self._events)

    def load_from(self, version: int) -> Iterable[DomainEvent]:
        return tuple(self._events[version:])
