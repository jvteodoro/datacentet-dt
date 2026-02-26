from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import MultiStreamCoordinator
from digital_twin.infrastructure.streaming.kafka_config import KafkaSettings
from digital_twin.infrastructure.streaming.kafka_consumer import KafkaConsumerAdapter

pytestmark = pytest.mark.kafka


class _AppendResult:
    def __init__(self, value: str) -> None:
        self.value = value


class _IdempotentStore:
    def __init__(self) -> None:
        self._seen: set[object] = set()
        self._events: list[tuple[int, object]] = []

    def append(self, event, **kwargs):
        ingest_id = kwargs.get("ingest_id")
        if ingest_id in self._seen:
            return _AppendResult("ALREADY_EXISTS")
        self._seen.add(ingest_id)
        self._events.append((kwargs["version_counter"], event))
        return _AppendResult("APPENDED")

    def load_all(self, **_kwargs):
        return tuple(event for _, event in self._events)

    def load_from(self, version: int, **_kwargs):
        return tuple(event for v, event in self._events if v > version)


class _Factory:
    def __call__(self, stream_id: str) -> DataCenterTwin:
        return DataCenterTwin(event_store=_IdempotentStore(), persistence_stream_id=stream_id)


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


def test_duplicate_ingest_id_is_skipped_on_second_consume() -> None:
    consumer = _FakeConsumer()
    producer = _FakeProducer()
    adapter = KafkaConsumerAdapter(
        settings=KafkaSettings(),
        coordinator=MultiStreamCoordinator(twin_factory=_Factory()),
        consumer=consumer,
        producer=producer,
    )

    payload = {
        "stream_id": "dc1",
        "ingest_id": "7dca2c75-a030-4960-968e-8c4f9652f0b3",
        "source": "iot",
        "source_time_utc": "2025-01-01T00:00:00Z",
        "event_type": "Tick",
        "payload": {"delta_time": 0.0},
    }

    msg = _Msg(value=json.dumps(payload).encode("utf-8"))
    adapter._handle_message(msg)
    adapter._handle_message(msg)

    assert consumer.commits == 2
    assert producer.messages == []
