from __future__ import annotations

from uuid import UUID

from digital_twin.infrastructure.streaming.kafka_consumer import KafkaMessageContext
from digital_twin.infrastructure.streaming.normalizer import OBSERVATION_METADATA_KEY, normalize_kafka_message


def test_normalizer_maps_kafka_to_domain_event() -> None:
    msg = {
        "stream_id": "dc1",
        "ingest_id": "f8f9acc8-1532-4a8b-93d0-e575f9f2d97b",
        "source": "iot_adapter",
        "source_time_utc": "2025-01-01T00:00:00Z",
        "event_type": "AddNode",
        "payload": {"node_id": "A"},
    }

    event, parsed = normalize_kafka_message(
        msg,
        default_stream_id="fallback",
        context=KafkaMessageContext(topic="dt.telemetry", partition=0, offset=12),
    )

    assert event.type == "AddNode"
    assert event.event_id == UUID(msg["ingest_id"])
    assert event.payload["node_id"] == "A"
    assert event.payload[OBSERVATION_METADATA_KEY]["kafka_offset"] == 12
    assert parsed.stream_id == "dc1"
