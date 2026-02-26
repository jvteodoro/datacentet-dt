from __future__ import annotations

import pytest

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import IngestionStatus, MultiStreamCoordinator

pytestmark = pytest.mark.kafka


class _Store:
    def __init__(self, stream_id: str) -> None:
        self.stream_id = stream_id
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
        self.stores: dict[str, _Store] = {}

    def __call__(self, stream_id: str) -> DataCenterTwin:
        store = _Store(stream_id)
        self.stores[stream_id] = store
        return DataCenterTwin(event_store=store, persistence_stream_id=stream_id)


def _add_node(stream_id: str, ingest_id: str, node_id: str, t: str) -> dict[str, object]:
    return {
        "stream_id": stream_id,
        "ingest_id": ingest_id,
        "source": "iot",
        "source_time_utc": t,
        "event_type": "AddNode",
        "payload": {"node_id": node_id},
    }


def test_ordering_is_preserved_per_stream_only() -> None:
    factory = _Factory()
    coordinator = MultiStreamCoordinator(twin_factory=factory)

    mixed = [
        _add_node("A", "11111111-1111-4111-8111-111111111111", "a1", "2025-01-01T00:00:00Z"),
        _add_node("B", "22222222-2222-4222-8222-222222222222", "b1", "2025-01-01T00:00:00Z"),
        _add_node("A", "33333333-3333-4333-8333-333333333333", "a2", "2025-01-01T00:00:01Z"),
        _add_node("B", "44444444-4444-4444-8444-444444444444", "b2", "2025-01-01T00:00:01Z"),
    ]

    outcomes = [
        coordinator.handle_message(msg, kafka_context={"topic": "t", "partition": idx % 2, "offset": idx})
        for idx, msg in enumerate(mixed)
    ]

    assert all(outcome.status is IngestionStatus.APPLIED for outcome in outcomes)

    stream_a_events = [event.payload["node_id"] for event in factory.stores["A"].load_all()]
    stream_b_events = [event.payload["node_id"] for event in factory.stores["B"].load_all()]

    assert stream_a_events == ["a1", "a2"]
    assert stream_b_events == ["b1", "b2"]
