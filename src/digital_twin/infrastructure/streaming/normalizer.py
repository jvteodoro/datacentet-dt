from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from digital_twin.domain.event import DomainEvent
from digital_twin.infrastructure.ingestion.normalize import OBSERVATION_METADATA_KEY, normalize_message_to_domain_event

from .message_schema import KafkaTelemetryMessage

if TYPE_CHECKING:
    from .kafka_consumer import KafkaMessageContext


def normalize_kafka_message(
    message: Mapping[str, Any],
    *,
    default_stream_id: str,
    context: KafkaMessageContext | None = None,
) -> tuple[DomainEvent, KafkaTelemetryMessage]:
    metadata = {
        "stream_id": str(message.get("stream_id") or default_stream_id),
        "source": str(message.get("source") or ""),
        "source_time_utc": str(message.get("source_time_utc") or ""),
        "kafka_partition": context.partition if context else None,
        "kafka_offset": context.offset if context else None,
    }
    return normalize_message_to_domain_event(
        message,
        default_stream_id=default_stream_id,
        require_ingest_id=False,
        observation_metadata=metadata,
    )
