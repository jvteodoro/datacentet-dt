from __future__ import annotations

import pytest

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import IngestionStatus, MultiStreamCoordinator

pytestmark = pytest.mark.kafka


class _AppendResult:
    def __init__(self, value: str) -> None:
        self.value = value


class _PerStreamStore:
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
        return DataCenterTwin(event_store=_PerStreamStore(), persistence_stream_id=stream_id)


def _msg(stream_id: str, ingest_id: str) -> dict[str, object]:
    return {
        "stream_id": stream_id,
        "ingest_id": ingest_id,
        "source": "iot",
        "source_time_utc": "2025-01-01T00:00:00Z",
        "event_type": "Tick",
        "payload": {"delta_time": 0.0},
    }


def test_duplicate_detection_is_scoped_per_stream() -> None:
    coordinator = MultiStreamCoordinator(twin_factory=_Factory())
    duplicated_id = "eb1ff37e-5878-4cbf-a72f-c4e60d8380f9"

    first = coordinator.handle_message(_msg("A", duplicated_id), kafka_context={"topic": "t", "partition": 0, "offset": 0})
    duplicate_a = coordinator.handle_message(
        _msg("A", duplicated_id),
        kafka_context={"topic": "t", "partition": 0, "offset": 1},
    )
    first_b = coordinator.handle_message(_msg("B", duplicated_id), kafka_context={"topic": "t", "partition": 1, "offset": 0})

    assert first.status is IngestionStatus.APPLIED
    assert duplicate_a.status is IngestionStatus.DUPLICATE
    assert first_b.status is IngestionStatus.APPLIED
