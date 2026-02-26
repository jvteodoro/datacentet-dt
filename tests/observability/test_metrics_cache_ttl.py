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
    def __init__(self) -> None:
        self.calls = 0

    def collect_metrics(self) -> dict[str, MetricPoint]:
        self.calls += 1
        return {
            "x": MetricPoint(kind=MetricKind.COUNTER, value=self.calls),
        }


def test_cache_ttl_avoids_refresh_for_repeated_gets() -> None:
    clock = _FakeClock()
    provider = _Provider()
    collector = SnapshotCollector((provider,), node_id="n", clock=clock)
    cache = MetricsSnapshotCache(collector=collector, ttl_ms=200, clock=clock)

    for _ in range(1000):
        cache.get(mode="LIVE")

    assert provider.calls <= 2


def test_cache_refreshes_after_ttl_expiry() -> None:
    clock = _FakeClock()
    provider = _Provider()
    collector = SnapshotCollector((provider,), node_id="n", clock=clock)
    cache = MetricsSnapshotCache(collector=collector, ttl_ms=200, clock=clock)

    cache.get(mode="LIVE")
    calls_after_first = provider.calls

    clock.advance_ms(250)
    cache.get(mode="LIVE")

    assert calls_after_first == 1
    assert provider.calls == 2
