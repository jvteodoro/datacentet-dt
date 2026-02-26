from __future__ import annotations

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import CoordinatorSettings, IngestionStatus, MultiStreamCoordinator


class _Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, delta: float) -> None:
        self.now += delta


class _Store:
    def __init__(self) -> None:
        self.events = []

    def append(self, event, **kwargs):
        self.events.append((kwargs["version_counter"], event))
        return None

    def load_all(self, **kwargs):
        _ = kwargs
        return tuple(e for _, e in self.events)

    def load_from(self, version: int, **kwargs):
        _ = kwargs
        return tuple(e for v, e in self.events if v > version)


class _Factory:
    def __init__(self) -> None:
        self.count = 0

    def __call__(self, stream_id: str) -> DataCenterTwin:
        self.count += 1
        return DataCenterTwin(event_store=_Store(), persistence_stream_id=stream_id)


def _msg(stream_id: str, ingest: str) -> dict[str, object]:
    return {
        "stream_id": stream_id,
        "ingest_id": ingest,
        "source": "iot",
        "source_time_utc": "2025-01-01T00:00:00Z",
        "event_type": "Tick",
        "payload": {"delta_time": 0.0},
    }


def test_ttl_eviction_and_reconstruction() -> None:
    clock = _Clock()
    factory = _Factory()
    coordinator = MultiStreamCoordinator(
        twin_factory=factory,
        settings=CoordinatorSettings(max_active_streams=10, stream_ttl_seconds=5, eviction_batch_size=50),
        monotonic_clock=clock,
    )

    outcome1 = coordinator.handle_message(_msg("A", "11111111-1111-4111-8111-111111111111"), kafka_context={"partition": 0, "offset": 0})
    assert outcome1.status is IngestionStatus.APPLIED
    assert coordinator.active_stream_count() == 1
    assert factory.count == 1

    clock.advance(6)
    evictions = coordinator.maybe_evict(now_monotonic=clock())
    assert len(evictions) == 1
    assert evictions[0].evicted is True
    assert coordinator.active_stream_count() == 0

    outcome2 = coordinator.handle_message(_msg("A", "22222222-2222-4222-8222-222222222222"), kafka_context={"partition": 0, "offset": 1})
    assert outcome2.status is IngestionStatus.APPLIED
    assert coordinator.active_stream_count() == 1
    assert factory.count == 2
