from __future__ import annotations

from uuid import UUID

import pytest

from digital_twin.infrastructure.streaming.message_schema import KafkaValidationError, parse_kafka_message


BASE = {
    "stream_id": "dc1",
    "ingest_id": "f8f9acc8-1532-4a8b-93d0-e575f9f2d97b",
    "source": "iot_adapter",
    "source_time_utc": "2025-01-01T00:00:00Z",
    "event_type": "AddNode",
    "payload": {"node_id": "A"},
}


def test_valid_message_parses() -> None:
    parsed = parse_kafka_message(BASE)
    assert parsed.stream_id == "dc1"
    assert isinstance(parsed.ingest_id, UUID)


def test_missing_ingest_id_is_generated() -> None:
    message = dict(BASE)
    message.pop("ingest_id")
    parsed = parse_kafka_message(message)
    assert isinstance(parsed.ingest_id, UUID)


def test_invalid_uuid_rejected() -> None:
    message = dict(BASE)
    message["ingest_id"] = "not-a-uuid"
    with pytest.raises(KafkaValidationError):
        parse_kafka_message(message)


def test_required_payload_fields_per_event_type() -> None:
    message = dict(BASE)
    message["event_type"] = "AddLink"
    message["payload"] = {"src": "A"}
    with pytest.raises(KafkaValidationError):
        parse_kafka_message(message)


def test_stream_id_is_mandatory_for_partitioning() -> None:
    message = dict(BASE)
    message.pop("stream_id")
    with pytest.raises(KafkaValidationError):
        parse_kafka_message(message)
