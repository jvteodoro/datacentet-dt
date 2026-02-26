from __future__ import annotations

import json
from dataclasses import dataclass

from digital_twin.infrastructure.streaming.coordinator import IngestionOutcome, IngestionStatus
from digital_twin.infrastructure.streaming.kafka_config import KafkaSettings
from digital_twin.infrastructure.streaming.kafka_consumer import KafkaConsumerAdapter


@dataclass
class _Msg:
    value: bytes
    partition: int = 0
    offset: int = 0
    topic: str = "dt.telemetry"


@dataclass
class _TP:
    topic: str
    partition: int


class _FakeConsumer:
    def __init__(self) -> None:
        self.commits = 0

    def subscribe(self, _topics, listener=None):
        self.listener = listener

    def commit(self):
        self.commits += 1

    def assignment(self):
        return {_TP(topic="dt.telemetry", partition=0)}


class _FakeProducer:
    def send(self, topic: str, value: bytes) -> None:
        _ = (topic, value)


class _Coordinator:
    def __init__(self):
        self.calls = 0
        self.metrics = type("M", (), {"set_kafka_lag_last": lambda self, value: None})()

    def handle_message(self, message, *, kafka_context):
        self.calls += 1
        return IngestionOutcome(
            stream_id=str(message.get("stream_id", "dc1")),
            ingest_id=str(message.get("ingest_id", "")),
            status=IngestionStatus.APPLIED,
            kafka_context=kafka_context,
        )


def test_no_processing_after_partition_revoked() -> None:
    consumer = _FakeConsumer()
    coordinator = _Coordinator()
    adapter = KafkaConsumerAdapter(
        settings=KafkaSettings(),
        coordinator=coordinator,
        consumer=consumer,
        producer=_FakeProducer(),
    )

    adapter.on_partitions_revoked([_TP(topic="dt.telemetry", partition=0)])
    msg = _Msg(
        value=json.dumps(
            {
                "stream_id": "dc1",
                "ingest_id": "11111111-1111-4111-8111-111111111111",
                "source": "iot",
                "source_time_utc": "2025-01-01T00:00:00Z",
                "event_type": "Tick",
                "payload": {"delta_time": 0.0},
            }
        ).encode("utf-8")
    )
    adapter._handle_message(msg)

    assert coordinator.calls == 0
