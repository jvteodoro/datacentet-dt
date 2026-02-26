from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from digital_twin.infrastructure.streaming.coordinator import MultiStreamCoordinator
from digital_twin.infrastructure.streaming.kafka_config import KafkaSettings
from digital_twin.infrastructure.streaming.kafka_consumer import KafkaConsumerAdapter

pytestmark = pytest.mark.kafka


@dataclass
class _Msg:
    value: bytes
    partition: int
    offset: int
    topic: str = "dt.telemetry"


class _FakeConsumer:
    def __init__(self) -> None:
        self.commits = 0

    def subscribe(self, _topics: list[str]) -> None:
        return

    def commit(self) -> None:
        self.commits += 1


class _FakeProducer:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bytes]] = []

    def send(self, topic: str, value: bytes) -> None:
        self.messages.append((topic, value))


def test_invalid_message_sent_to_dlq_and_loop_survives() -> None:
    consumer = _FakeConsumer()
    producer = _FakeProducer()
    settings = KafkaSettings(dlq_topic="dt.telemetry.dlq")
    adapter = KafkaConsumerAdapter(
        settings=settings,
        coordinator=MultiStreamCoordinator(twin_factory=lambda _s: None),
        consumer=consumer,
        producer=producer,
    )

    invalid = {
        "stream_id": "dc1",
        "source": "iot",
        "source_time_utc": "2025-01-01T00:00:00Z",
        "event_type": "AddLink",
        "payload": {"src": "A"},
    }

    adapter._handle_message(_Msg(value=json.dumps(invalid).encode("utf-8"), partition=0, offset=10))

    assert consumer.commits == 1
    assert len(producer.messages) == 1
    topic, payload = producer.messages[0]
    decoded = json.loads(payload.decode("utf-8"))
    assert topic == "dt.telemetry.dlq"
    assert "payload missing required fields" in decoded["error"]
