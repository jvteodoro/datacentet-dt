from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import MultiStreamCoordinator
from digital_twin.infrastructure.streaming.kafka_config import KafkaSettings
from digital_twin.infrastructure.streaming.kafka_consumer import KafkaConsumerAdapter

pytestmark = pytest.mark.kafka


class _Store:
    def __init__(self) -> None:
        self.events: list[tuple[int, object]] = []

    def append(self, event, **kwargs):
        self.events.append((kwargs["version_counter"], event))
        return None

    def load_all(self, **_kwargs):
        return tuple(event for _, event in self.events)

    def load_from(self, version: int, **_kwargs):
        return tuple(event for v, event in self.events if v > version)


class _Factory:
    def __init__(self) -> None:
        self.twin = DataCenterTwin(event_store=_Store(), persistence_stream_id="dc1")

    def __call__(self, stream_id: str) -> DataCenterTwin:
        assert stream_id == "dc1"
        return self.twin


@dataclass
class _Msg:
    value: bytes
    partition: int
    offset: int
    topic: str = "dt.telemetry"


class _FakeConsumer:
    def subscribe(self, _topics: list[str]) -> None:
        return

    def commit(self) -> None:
        return


class _FakeProducer:
    def send(self, topic: str, value: bytes) -> None:
        _ = (topic, value)


def test_single_partition_messages_processed_in_order() -> None:
    factory = _Factory()
    adapter = KafkaConsumerAdapter(
        settings=KafkaSettings(),
        coordinator=MultiStreamCoordinator(twin_factory=factory),
        consumer=_FakeConsumer(),
        producer=_FakeProducer(),
    )

    events = [
        {
            "stream_id": "dc1",
            "ingest_id": "7dca2c75-a030-4960-968e-8c4f9652f0b3",
            "source": "iot",
            "source_time_utc": "2025-01-01T00:00:00Z",
            "event_type": "AddNode",
            "payload": {"node_id": "A"},
        },
        {
            "stream_id": "dc1",
            "ingest_id": "89fd0e64-4fef-4adf-981d-e1f6324d1389",
            "source": "iot",
            "source_time_utc": "2025-01-01T00:00:01Z",
            "event_type": "AddNode",
            "payload": {"node_id": "B"},
        },
    ]

    for idx, event in enumerate(events):
        adapter._handle_message(_Msg(value=json.dumps(event).encode("utf-8"), partition=0, offset=idx))

    assert [event.payload["node_id"] for event in factory.twin.event_log] == ["A", "B"]
