from __future__ import annotations

from digital_twin.infrastructure.ingestion.normalize import normalize_message_to_domain_event
from digital_twin.infrastructure.streaming.kafka_consumer import KafkaMessageContext
from digital_twin.infrastructure.streaming.normalizer import normalize_kafka_message


def test_kafka_and_shared_normalizers_produce_equivalent_domain_event() -> None:
    message = {
        "stream_id": "dc7",
        "ingest_id": "f8f9acc8-1532-4a8b-93d0-e575f9f2d97b",
        "source": "iot_adapter",
        "source_time_utc": "2026-01-01T00:00:00Z",
        "event_type": "AddNode",
        "payload": {"node_id": "A"},
    }

    kafka_event, kafka_parsed = normalize_kafka_message(
        message,
        default_stream_id="dc1",
        context=KafkaMessageContext(topic="dt.telemetry", partition=1, offset=9),
    )
    shared_event, shared_parsed = normalize_message_to_domain_event(
        message,
        default_stream_id="dc1",
        require_ingest_id=False,
        observation_metadata={
            "stream_id": "dc7",
            "source": "iot_adapter",
            "source_time_utc": "2026-01-01T00:00:00Z",
            "kafka_partition": 1,
            "kafka_offset": 9,
        },
    )

    assert kafka_parsed == shared_parsed
    assert kafka_event.event_id == shared_event.event_id
    assert kafka_event.type == shared_event.type
    assert kafka_event.payload == shared_event.payload
