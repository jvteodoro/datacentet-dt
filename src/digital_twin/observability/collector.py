from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .clock import Clock, DefaultClock
from .model import Histogram, MetricPoint, MetricsSnapshot, TopKEntry


class MetricsProvider(Protocol):
    def collect_metrics(self) -> dict[str, MetricPoint]:
        ...

    def collect_topk(self) -> dict[str, tuple[TopKEntry, ...]]:
        ...

    def collect_histograms(self) -> dict[str, Histogram]:
        ...


@dataclass(slots=True)
class SnapshotCollector:
    providers: tuple[MetricsProvider, ...]
    node_id: str | None = None
    clock: Clock = field(default_factory=DefaultClock)

    def collect(self, *, mode: str) -> MetricsSnapshot:
        combined: dict[str, MetricPoint] = {}
        topk: dict[str, tuple[TopKEntry, ...]] = {}
        histograms: dict[str, Histogram] = {}
        for provider in self.providers:
            combined.update(provider.collect_metrics())
            if hasattr(provider, "collect_topk"):
                topk.update(provider.collect_topk())
            if hasattr(provider, "collect_histograms"):
                histograms.update(provider.collect_histograms())
        return MetricsSnapshot(
            timestamp_utc=self.clock.now_utc_rfc3339(),
            node_id=self.node_id,
            mode=mode.upper(),
            metrics=combined,
            topk=topk,
            histograms=histograms,
        )
