from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .clock import Clock, DefaultClock
from .model import MetricPoint, MetricsSnapshot


class MetricsProvider(Protocol):
    def collect_metrics(self) -> dict[str, MetricPoint]:
        ...


@dataclass(slots=True)
class SnapshotCollector:
    providers: tuple[MetricsProvider, ...]
    node_id: str | None = None
    clock: Clock = field(default_factory=DefaultClock)

    def collect(self, *, mode: str) -> MetricsSnapshot:
        combined: dict[str, MetricPoint] = {}
        for provider in self.providers:
            combined.update(provider.collect_metrics())
        return MetricsSnapshot(
            timestamp_utc=self.clock.now_utc_rfc3339(),
            node_id=self.node_id,
            mode=mode.upper(),
            metrics=combined,
        )
