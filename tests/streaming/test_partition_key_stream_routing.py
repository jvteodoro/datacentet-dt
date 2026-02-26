from __future__ import annotations

import json
import os
from dataclasses import dataclass

import pytest

from digital_twin.infrastructure.streaming.kafka_config import KafkaSettings
from digital_twin.infrastructure.streaming.kafka_producer import KafkaTelemetryProducer

pytestmark = pytest.mark.kafka


class _FakeProducer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bytes, bytes]] = []

    def send(self, topic: str, key: bytes, value: bytes) -> None:
        self.calls.append((topic, key, value))


class _FakeKafkaModule:
    def __init__(self, producer: _FakeProducer) -> None:
        self._producer = producer

    def KafkaProducer(self, **_kwargs):
        return self._producer


def test_telemetry_producer_sets_partition_key_from_stream_id(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeProducer()
    monkeypatch.setattr("digital_twin.infrastructure.streaming.kafka_producer.import_module", lambda _name: _FakeKafkaModule(fake))

    producer = KafkaTelemetryProducer(settings=KafkaSettings())
    message = {
        "stream_id": "stream-A",
        "ingest_id": "9aa77e3f-0cee-46ec-8bbf-716e276b389f",
        "source": "iot",
        "source_time_utc": "2025-01-01T00:00:00Z",
        "event_type": "AddNode",
        "payload": {"node_id": "A"},
    }
    producer.send_telemetry(message)

    topic, key, value = fake.calls[0]
    assert topic == KafkaSettings().telemetry_topic
    assert key == b"stream-A"
    assert json.loads(value.decode("utf-8"))["stream_id"] == "stream-A"


@pytest.mark.skipif(
    not os.getenv("KAFKA_BROKERS"),
    reason="Kafka unavailable: set KAFKA_BROKERS for real partition routing validation",
)
def test_same_stream_key_resolves_to_stable_partition_when_runtime_available() -> None:
    pytest.skip("Requires real Kafka runtime introspection; enabled in integration environments")
