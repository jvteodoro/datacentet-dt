from __future__ import annotations

from dataclasses import dataclass

from .base_event import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True, eq=False, repr=False)
class WorkloadSubmittedEvent(DomainEvent):
    workload_id: str
    source: str

    def _event_marker(self) -> None:
        return None


@dataclass(frozen=True, slots=True, kw_only=True, eq=False, repr=False)
class WorkloadDeliveredEvent(DomainEvent):
    workload_id: str
    source: str
    destination: str
    required_cycles: float = 1.0

    def _event_marker(self) -> None:
        return None
