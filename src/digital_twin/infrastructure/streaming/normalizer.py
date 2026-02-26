from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from digital_twin.domain.event import DomainEvent

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .kafka_consumer import KafkaMessageContext
from .message_schema import KafkaTelemetryMessage, parse_kafka_message


OBSERVATION_METADATA_KEY = "_ingest_observation"


def normalize_kafka_message(
    message: Mapping[str, Any],
    *,
    default_stream_id: str,
    context: KafkaMessageContext | None = None,
) -> tuple[DomainEvent, KafkaTelemetryMessage]:
    parsed = parse_kafka_message(dict(message), default_stream_id=default_stream_id)

    payload = dict(parsed.payload)
    payload[OBSERVATION_METADATA_KEY] = {
        "stream_id": parsed.stream_id,
        "source": parsed.source,
        "source_time_utc": parsed.source_time_utc,
        "kafka_partition": context.partition if context else None,
        "kafka_offset": context.offset if context else None,
    }

    event = DomainEvent(
        timestamp=0,
        type=parsed.event_type,
        payload=payload,
        event_id=parsed.ingest_id,
    )
    return event, parsed
