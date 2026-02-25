from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID, NAMESPACE_URL, uuid5


EVENT_CONTROL_ACTION_PROPOSED = "ControlActionProposed"


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Canonical immutable domain event."""

    timestamp: int
    type: str
    payload: Mapping[str, Any]
    version: int = 1
    event_id: UUID = field(default=None)

    def __post_init__(self) -> None:
        normalized_payload = _immutable_payload(self.payload)
        object.__setattr__(self, "payload", normalized_payload)

        if self.event_id is None:
            object.__setattr__(
                self,
                "event_id",
                _deterministic_event_id(
                    timestamp=self.timestamp,
                    event_type=self.type,
                    payload=normalized_payload,
                    version=self.version,
                ),
            )


def normalize_event(event: DomainEvent) -> DomainEvent:
    """Normalization hook for canonical ingestion (placeholder for Phase 1)."""

    return DomainEvent(
        event_id=event.event_id,
        timestamp=event.timestamp,
        type=event.type.strip(),
        payload=event.payload,
        version=event.version,
    )


def _immutable_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(payload))


def _deterministic_event_id(
    *,
    timestamp: int,
    event_type: str,
    payload: Mapping[str, Any],
    version: int,
) -> UUID:
    try:
        payload_token = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    except TypeError:
        payload_token = repr(sorted(payload.items()))

    canonical_token = f"{timestamp}|{event_type}|{version}|{payload_token}"
    return uuid5(NAMESPACE_URL, canonical_token)
