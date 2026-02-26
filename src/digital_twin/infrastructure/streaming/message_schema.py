from __future__ import annotations

from digital_twin.infrastructure.ingestion.message_contract import (
    TelemetryMessage as KafkaTelemetryMessage,
)
from digital_twin.infrastructure.ingestion.message_contract import (
    TelemetryValidationError as KafkaValidationError,
)
from digital_twin.infrastructure.ingestion.message_contract import validate_message


def parse_kafka_message(message: dict[str, object], *, default_stream_id: str | None = None) -> KafkaTelemetryMessage:
    """Backward-compatible wrapper for Kafka telemetry schema parsing."""

    return validate_message(message, default_stream_id=default_stream_id, require_ingest_id=False)
