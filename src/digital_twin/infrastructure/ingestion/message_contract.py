from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


class TelemetryValidationError(ValueError):
    """Raised when an ingestion message fails schema validation."""


_EVENT_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "AddNode": ("node_id",),
    "AddLink": ("src", "dst", "capacity"),
    "FlowStarted": ("flow_id", "src", "dst", "path", "rate", "size"),
    "FlowEnded": ("flow_id",),
    "WorkloadStarted": ("workload_id", "server_id", "cpu_demand", "memory_demand", "remaining_size"),
    "WorkloadEnded": ("workload_id",),
    "Tick": ("delta_time",),
}


@dataclass(frozen=True, slots=True)
class TelemetryMessage:
    """Canonical ingestion message contract shared by HTTP and Kafka paths."""

    stream_id: str
    ingest_id: UUID
    source: str
    source_time_utc: str
    event_type: str
    payload: dict[str, Any]


def validate_message(
    message: dict[str, Any],
    *,
    default_stream_id: str | None = None,
    require_ingest_id: bool = False,
) -> TelemetryMessage:
    """Validate and normalize a telemetry message into the shared contract."""

    stream_id = str(message.get("stream_id") or default_stream_id or "").strip()
    if not stream_id:
        raise TelemetryValidationError("stream_id is required")

    ingest_id_raw = message.get("ingest_id")
    if ingest_id_raw is None:
        if require_ingest_id:
            raise TelemetryValidationError("ingest_id is required")
        ingest_id = uuid4()
    else:
        try:
            ingest_id = UUID(str(ingest_id_raw))
        except ValueError as exc:
            raise TelemetryValidationError("ingest_id must be a valid UUID") from exc

    source = str(message.get("source") or "").strip()
    if not source:
        raise TelemetryValidationError("source is required")

    source_time_utc = str(message.get("source_time_utc") or "").strip()
    if not source_time_utc:
        raise TelemetryValidationError("source_time_utc is required")
    _validate_rfc3339(source_time_utc)

    event_type = str(message.get("event_type") or "").strip()
    if not event_type:
        raise TelemetryValidationError("event_type is required")

    payload_raw = message.get("payload")
    if not isinstance(payload_raw, dict):
        raise TelemetryValidationError("payload must be a JSON object")

    required_fields = _EVENT_REQUIRED_FIELDS.get(event_type)
    if required_fields is not None:
        missing = [field for field in required_fields if field not in payload_raw]
        if missing:
            raise TelemetryValidationError(f"payload missing required fields for {event_type}: {', '.join(missing)}")

    return TelemetryMessage(
        stream_id=stream_id,
        ingest_id=ingest_id,
        source=source,
        source_time_utc=source_time_utc,
        event_type=event_type,
        payload=dict(payload_raw),
    )


def _validate_rfc3339(value: str) -> None:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise TelemetryValidationError("source_time_utc must be RFC3339") from exc
