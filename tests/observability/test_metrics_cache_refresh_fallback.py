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


class _FlakyProvider:
    def __init__(self) -> None:
        self.calls = 0

    def collect_metrics(self) -> dict[str, MetricPoint]:
        self.calls += 1
        if self.calls > 1:
            raise RuntimeError("refresh failed")
        return {"a": MetricPoint(kind=MetricKind.COUNTER, value=1)}


def test_refresh_failure_returns_last_snapshot_and_increments_error_counter() -> None:
    clock = _FakeClock()
    provider = _FlakyProvider()
    collector = SnapshotCollector((provider,), node_id="n", clock=clock)
    cache = MetricsSnapshotCache(collector=collector, ttl_ms=100, clock=clock)

    ok = cache.get(mode="LIVE")
    assert int(ok.metrics["observability.cache_refresh_errors_total"].value) == 0

    clock.advance_ms(150)
    fallback = cache.get(mode="LIVE")

    assert fallback.metrics["a"].value == 1
    assert int(fallback.metrics["observability.cache_refresh_errors_total"].value) == 1
