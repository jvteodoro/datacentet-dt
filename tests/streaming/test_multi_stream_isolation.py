from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import IngestionStatus, MultiStreamCoordinator
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


class _TwinFactory:
    def __init__(self) -> None:
        self.by_stream: dict[str, DataCenterTwin] = {}

    def __call__(self, stream_id: str) -> DataCenterTwin:
        twin = DataCenterTwin(event_store=_Store(), persistence_stream_id=stream_id)
        self.by_stream[stream_id] = twin
        return twin


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


def test_multi_stream_isolation() -> None:
    factory = _TwinFactory()
    coordinator = MultiStreamCoordinator(twin_factory=factory)
    adapter = KafkaConsumerAdapter(
        settings=KafkaSettings(),
        coordinator=coordinator,
        consumer=_FakeConsumer(),
        producer=_FakeProducer(),
    )

    messages = [
        {
            "stream_id": "A",
            "ingest_id": "43ec7f6d-78b0-43d3-84d8-fb67f8deab64",
            "source": "iot",
            "source_time_utc": "2025-01-01T00:00:00Z",
            "event_type": "AddNode",
            "payload": {"node_id": "n1"},
        },
        {
            "stream_id": "B",
            "ingest_id": "ab806b2f-17cf-47dc-9bb2-d93f66084f33",
            "source": "iot",
            "source_time_utc": "2025-01-01T00:00:01Z",
            "event_type": "AddNode",
            "payload": {"node_id": "n2"},
        },
    ]

    for idx, payload in enumerate(messages):
        adapter._handle_message(_Msg(value=json.dumps(payload).encode("utf-8"), partition=idx, offset=idx))

    assert set(factory.by_stream.keys()) == {"A", "B"}
    assert len(factory.by_stream["A"].event_log) == 1
    assert len(factory.by_stream["B"].event_log) == 1
    assert factory.by_stream["A"] is not factory.by_stream["B"]


def test_coordinator_outcome_applied() -> None:
    coordinator = MultiStreamCoordinator(twin_factory=_TwinFactory())
    outcome = coordinator.handle_message(
        {
            "stream_id": "A",
            "ingest_id": "45f17096-1ef6-49f6-8af4-78d2ac6ea8ac",
            "source": "iot",
            "source_time_utc": "2025-01-01T00:00:00Z",
            "event_type": "AddNode",
            "payload": {"node_id": "n1"},
        },
        kafka_context={"topic": "dt.telemetry", "partition": 0, "offset": 10},
    )
    assert outcome.status is IngestionStatus.APPLIED
