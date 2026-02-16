from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from math import isfinite
from numbers import Real
from time import time
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class DomainEvent(ABC):
    event_id: UUID = field(default_factory=uuid4)
    timestamp: float = field(default_factory=time)

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, UUID):
            raise TypeError("event_id must be a UUID")

        if not isinstance(self.timestamp, Real):
            raise TypeError("timestamp must be a real scalar")

        if not isfinite(float(self.timestamp)):
            raise ValueError("timestamp must be finite")

    @abstractmethod
    def _event_marker(self) -> None:
        """Marker method to enforce subclassing of concrete domain events."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DomainEvent):
            return NotImplemented
        return self.event_id == other.event_id

    def __hash__(self) -> int:
        return hash(self.event_id)

    def __lt__(self, other: DomainEvent) -> bool:
        if not isinstance(other, DomainEvent):
            return NotImplemented
        return self.timestamp < other.timestamp

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(event_id={self.event_id}, "
            f"timestamp={self.timestamp})"
        )
