from __future__ import annotations

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import CoordinatorSettings, IngestionStatus, MultiStreamCoordinator
from digital_twin.infrastructure.streaming.streaming_metrics import StreamingMetricsCollector


class _AppendResult:
    def __init__(self, value: str) -> None:
        self.value = value


class _Store:
    def __init__(self) -> None:
        self.events = []
        self.seen = set()

    def append(self, event, **kwargs):
        ingest_id = kwargs.get("ingest_id")
        if ingest_id in self.seen:
            return _AppendResult("ALREADY_EXISTS")
        self.seen.add(ingest_id)
        self.events.append((kwargs["version_counter"], event))
        return _AppendResult("APPENDED")

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


def test_metrics_are_observational_and_outcomes_stable() -> None:
    metrics = StreamingMetricsCollector()
    coordinator = MultiStreamCoordinator(
        twin_factory=_Factory(),
        settings=CoordinatorSettings(max_active_streams=4, stream_ttl_seconds=60, eviction_batch_size=100),
        metrics=metrics,
    )

    out1 = coordinator.handle_message(_msg("A", "11111111-1111-4111-8111-111111111111"), kafka_context={"partition": 0, "offset": 0})
    out2 = coordinator.handle_message(_msg("A", "11111111-1111-4111-8111-111111111111"), kafka_context={"partition": 0, "offset": 1})

    assert out1.status is IngestionStatus.APPLIED
    assert out2.status is IngestionStatus.DUPLICATE

    snap = metrics.snapshot()
    assert snap.ingestion_outcome_total["APPLIED"] >= 1
    assert snap.ingestion_outcome_total["DUPLICATE"] >= 1
    assert snap.streams_active_gauge == 1
    assert snap.coordinator_handle_latency_ms_last >= 0.0
