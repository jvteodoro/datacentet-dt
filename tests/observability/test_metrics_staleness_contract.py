from __future__ import annotations

from digital_twin.observability.cache import MetricsSnapshotCache
from digital_twin.observability.clock import Clock
from digital_twin.observability.collector import SnapshotCollector
from digital_twin.observability.model import MetricKind, MetricPoint


class _FakeClock(Clock):
    def __init__(self) -> None:
        self.monotonic = 0.0

    def now_monotonic(self) -> float:
        return self.monotonic

    def now_utc_rfc3339(self) -> str:
        return "2026-01-01T00:00:00Z"

    def advance_ms(self, value: int) -> None:
        self.monotonic += value / 1000.0


class _Provider:
    def collect_metrics(self) -> dict[str, MetricPoint]:
        return {"y": MetricPoint(kind=MetricKind.GAUGE, value=1)}


def test_staleness_contract_exposes_produced_at_and_age_bounded_by_ttl() -> None:
    ttl_ms = 200
    epsilon_ms = 1.0
    clock = _FakeClock()
    collector = SnapshotCollector((_Provider(),), node_id="n", clock=clock)
    cache = MetricsSnapshotCache(collector=collector, ttl_ms=ttl_ms, clock=clock)

    first = cache.get(mode="LIVE")
    assert first.produced_at_utc is not None
    assert first.snapshot_age_ms is not None

    clock.advance_ms(150)
    second = cache.get(mode="LIVE")

    assert second.produced_at_utc is not None
    assert second.snapshot_age_ms is not None
    assert second.snapshot_age_ms <= ttl_ms + epsilon_ms
