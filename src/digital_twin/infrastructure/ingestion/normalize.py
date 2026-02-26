from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from digital_twin.domain.event import DomainEvent

from .message_contract import TelemetryMessage, validate_message

OBSERVATION_METADATA_KEY = "_ingest_observation"


def normalize_message_to_domain_event(
    message: Mapping[str, Any],
    *,
    default_stream_id: str,
    require_ingest_id: bool = False,
    observation_metadata: dict[str, Any] | None = None,
) -> tuple[DomainEvent, TelemetryMessage]:
    """Convert a raw telemetry message to a DomainEvent deterministically."""

    parsed = validate_message(
        dict(message),
        default_stream_id=default_stream_id,
        require_ingest_id=require_ingest_id,
    )
    payload = dict(parsed.payload)
    if observation_metadata is not None:
        payload[OBSERVATION_METADATA_KEY] = dict(observation_metadata)

    event = DomainEvent(
        timestamp=0,
        type=parsed.event_type,
        payload=payload,
        event_id=parsed.ingest_id,
    )
    return event, parsed
