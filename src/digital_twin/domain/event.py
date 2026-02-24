from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Canonical immutable domain event."""

    timestamp: int
    type: str
    payload: Mapping[str, Any]
    version: int = 1
    event_id: UUID = field(default_factory=uuid4)


def normalize_event(event: DomainEvent) -> DomainEvent:
    """Normalization hook for canonical ingestion (placeholder for Phase 1)."""

    return event
