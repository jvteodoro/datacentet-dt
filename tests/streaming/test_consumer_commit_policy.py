from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from digital_twin.infrastructure.streaming.coordinator import IngestionOutcome, IngestionStatus
from digital_twin.infrastructure.streaming.kafka_config import KafkaSettings
from digital_twin.infrastructure.streaming.kafka_consumer import KafkaConsumerAdapter

pytestmark = pytest.mark.kafka


@dataclass
class _Msg:
    value: bytes
    partition: int = 0
    offset: int = 0
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


class _OutcomeCoordinator:
    def __init__(self, status: IngestionStatus) -> None:
        self._status = status

    def handle_message(self, message: dict[str, object], *, kafka_context: dict[str, object]) -> IngestionOutcome:
        return IngestionOutcome(
            stream_id=str(message.get("stream_id", "dc1")),
            ingest_id=str(message.get("ingest_id", "")),
            status=self._status,
            kafka_context=kafka_context,
            dlq_reason="bad message" if self._status is IngestionStatus.DLQ else None,
            raw_message=message if self._status is IngestionStatus.DLQ else None,
        )


BASE_MSG = {
    "stream_id": "dc1",
    "ingest_id": "b6616cd3-8918-4f6a-97f2-38015ce50a26",
    "source": "iot",
    "source_time_utc": "2025-01-01T00:00:00Z",
    "event_type": "AddNode",
    "payload": {"node_id": "A"},
}


def test_commit_happens_for_applied_duplicate_and_dlq() -> None:
    for status in (IngestionStatus.APPLIED, IngestionStatus.DUPLICATE, IngestionStatus.DLQ):
        consumer = _FakeConsumer()
        producer = _FakeProducer()
        adapter = KafkaConsumerAdapter(
            settings=KafkaSettings(),
            coordinator=_OutcomeCoordinator(status),
            consumer=consumer,
            producer=producer,
        )
        adapter._handle_message(_Msg(value=json.dumps(BASE_MSG).encode("utf-8")))
        assert consumer.commits == 1


def test_version_conflict_raises_and_does_not_commit() -> None:
    consumer = _FakeConsumer()
    adapter = KafkaConsumerAdapter(
        settings=KafkaSettings(),
        coordinator=_OutcomeCoordinator(IngestionStatus.VERSION_CONFLICT),
        consumer=consumer,
        producer=_FakeProducer(),
    )

    with pytest.raises(RuntimeError):
        adapter._handle_message(_Msg(value=json.dumps(BASE_MSG).encode("utf-8")))

    assert consumer.commits == 0
