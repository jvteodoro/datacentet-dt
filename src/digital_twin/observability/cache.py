from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from .clock import Clock
from .collector import SnapshotCollector
from .model import MetricKind, MetricPoint, MetricsSnapshot


@dataclass(slots=True)
class _CacheState:
    snapshot: MetricsSnapshot | None = None
    produced_at_monotonic: float = 0.0


class MetricsSnapshotCache:
    def __init__(self, collector: SnapshotCollector, ttl_ms: int, clock: Clock) -> None:
        if ttl_ms <= 0:
            raise ValueError("ttl_ms must be > 0")
        self._collector = collector
        self._ttl_s = ttl_ms / 1000.0
        self._clock = clock
        self._state = _CacheState()
        self._lock = Lock()
        self._refresh_errors_total = 0

    def get(self, *, mode: str) -> MetricsSnapshot:
        now = self._clock.now_monotonic()
        with self._lock:
            cached = self._state.snapshot
            produced_at = self._state.produced_at_monotonic
            if cached is not None and (now - produced_at) <= self._ttl_s:
                return self._decorate_snapshot(cached, produced_at, now)

        return self.refresh(mode=mode)

    def refresh(self, *, mode: str) -> MetricsSnapshot:
        now = self._clock.now_monotonic()
        try:
            fresh = self._collector.collect(mode=mode)
        except Exception:
            with self._lock:
                self._refresh_errors_total += 1
                if self._state.snapshot is not None:
                    fallback_now = self._clock.now_monotonic()
                    return self._decorate_snapshot(self._state.snapshot, self._state.produced_at_monotonic, fallback_now)
            raise

        produced_at_utc = self._clock.now_utc_rfc3339()
        with self._lock:
            self._state.snapshot = MetricsSnapshot(
                timestamp_utc=fresh.timestamp_utc,
                produced_at_utc=produced_at_utc,
                mode=fresh.mode,
                metrics=dict(fresh.metrics),
                node_id=fresh.node_id,
                topk=dict(fresh.topk),
                histograms=dict(fresh.histograms),
            )
            self._state.produced_at_monotonic = now
            return self._decorate_snapshot(self._state.snapshot, now, now)

    def _decorate_snapshot(self, snapshot: MetricsSnapshot, produced_at: float, now: float) -> MetricsSnapshot:
        age_ms = max(0.0, (now - produced_at) * 1000.0)
        metrics = dict(snapshot.metrics)
        metrics["observability.cache_refresh_errors_total"] = MetricPoint(
            kind=MetricKind.COUNTER,
            value=self._refresh_errors_total,
            unit="errors",
            description="Total cache refresh failures.",
        )
        return MetricsSnapshot(
            timestamp_utc=snapshot.timestamp_utc,
            produced_at_utc=snapshot.produced_at_utc,
            mode=snapshot.mode,
            metrics=metrics,
            node_id=snapshot.node_id,
            snapshot_age_ms=age_ms,
            topk=dict(snapshot.topk),
            histograms=dict(snapshot.histograms),
        )
