from __future__ import annotations

from collections.abc import Iterable

from digital_twin.application.ports.event_store import EventStore
from digital_twin.domain.event import DomainEvent


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        self._events: list[tuple[int, DomainEvent]] = []

    def append(self, event: DomainEvent, **kwargs: object) -> None:
        version_counter = int(kwargs.get("version_counter", event.version))
        self._events.append((version_counter, event))

    def load_all(self, **_: object) -> Iterable[DomainEvent]:
        return tuple(event for _, event in self._events)

    def load_from(self, version: int, **_: object) -> Iterable[DomainEvent]:
        return tuple(event for version_counter, event in self._events if version_counter > version)
