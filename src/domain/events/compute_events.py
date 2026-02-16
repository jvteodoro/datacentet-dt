from __future__ import annotations

from dataclasses import dataclass

from .base_event import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True, eq=False, repr=False)
class TaskStartedEvent(DomainEvent):
    task_id: str
    node_id: str

    def _event_marker(self) -> None:
        return None


@dataclass(frozen=True, slots=True, kw_only=True, eq=False, repr=False)
class TaskCompletedEvent(DomainEvent):
    task_id: str
    node_id: str

    def _event_marker(self) -> None:
        return None
