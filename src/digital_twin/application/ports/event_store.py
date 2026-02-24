from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from digital_twin.domain.event import DomainEvent


class EventStore(ABC):
    @abstractmethod
    def append(self, event: DomainEvent) -> None:
        """Append one canonical domain event."""

    @abstractmethod
    def load_all(self) -> Iterable[DomainEvent]:
        """Load all persisted events in insertion order."""

    @abstractmethod
    def load_from(self, version: int) -> Iterable[DomainEvent]:
        """Load events with state version strictly greater than ``version``."""
