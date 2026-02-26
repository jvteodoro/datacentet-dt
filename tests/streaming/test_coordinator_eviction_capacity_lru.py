from __future__ import annotations

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import CoordinatorSettings, MultiStreamCoordinator


class _Clock:
    def __init__(self) -> None:
        self.now = 2000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, delta: float = 1.0) -> None:
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
    def __call__(self, stream_id: str) -> DataCenterTwin:
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


def test_capacity_lru_eviction() -> None:
    clock = _Clock()
    coordinator = MultiStreamCoordinator(
        twin_factory=_Factory(),
        settings=CoordinatorSettings(max_active_streams=2, stream_ttl_seconds=1000, eviction_batch_size=100),
        monotonic_clock=clock,
    )

    coordinator.handle_message(_msg("A", "11111111-1111-4111-8111-111111111111"), kafka_context={"partition": 0, "offset": 0})
    clock.advance()
    coordinator.handle_message(_msg("B", "22222222-2222-4222-8222-222222222222"), kafka_context={"partition": 1, "offset": 0})
    clock.advance()
    coordinator.handle_message(_msg("C", "33333333-3333-4333-8333-333333333333"), kafka_context={"partition": 2, "offset": 0})

    assert coordinator.active_stream_count() == 2
    active = set(coordinator.twins.keys())
    assert active == {"B", "C"}

    snapshot = coordinator.metrics.snapshot()
    assert snapshot.streams_evicted_total >= 1
    assert snapshot.streams_evicted_capacity_total >= 1
