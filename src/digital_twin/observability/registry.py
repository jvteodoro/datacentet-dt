from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from digital_twin.domain.metrics import MetricsCollector
from digital_twin.infrastructure.streaming.streaming_metrics import StreamingMetricsCollector

if TYPE_CHECKING:
    from digital_twin.infrastructure.db.metrics import DBAdapterMetrics

from .collector import MetricsProvider, SnapshotCollector
from .model import MetricKind, MetricPoint, MetricsSnapshot


@dataclass(slots=True)
class DomainMetricsProvider:
    collector: MetricsCollector

    def collect_metrics(self) -> dict[str, MetricPoint]:
        total = self.collector.events_processed_total
        avg_ns = (self.collector.total_event_latency_ns / total) if total else 0.0
        return {
            "domain.events_processed_total": MetricPoint(
                kind=MetricKind.COUNTER,
                value=total,
                unit="events",
                description="Total ingested domain events.",
            ),
            "domain.ingestion_latency_ns_last": MetricPoint(
                kind=MetricKind.GAUGE,
                value=self.collector.last_event_latency_ns,
                unit="ns",
                description="Most recent ingestion latency measured at boundary.",
            ),
            "domain.ingestion_latency_ns_avg": MetricPoint(
                kind=MetricKind.GAUGE,
                value=avg_ns,
                unit="ns",
                description="Average ingestion latency measured at boundary.",
            ),
        }


@dataclass(slots=True)
class StreamingMetricsProvider:
    collector: StreamingMetricsCollector

    def collect_metrics(self) -> dict[str, MetricPoint]:
        snap = self.collector.snapshot()
        metrics: dict[str, MetricPoint] = {
            "streaming.streams_active": MetricPoint(
                kind=MetricKind.GAUGE,
                value=snap.streams_active_gauge,
                unit="streams",
                description="Active stream coordinators in memory.",
            ),
            "streaming.evictions_total": MetricPoint(
                kind=MetricKind.COUNTER,
                value=snap.streams_evicted_total,
                unit="streams",
                description="Total stream evictions.",
            ),
            "streaming.evictions_ttl_total": MetricPoint(
                kind=MetricKind.COUNTER,
                value=snap.streams_evicted_ttl_total,
                unit="streams",
                description="Total stream evictions by TTL.",
            ),
            "streaming.evictions_capacity_total": MetricPoint(
                kind=MetricKind.COUNTER,
                value=snap.streams_evicted_capacity_total,
                unit="streams",
                description="Total stream evictions by capacity.",
            ),
            "streaming.handle_latency_ms_last": MetricPoint(
                kind=MetricKind.GAUGE,
                value=snap.coordinator_handle_latency_ms_last,
                unit="ms",
                description="Last coordinator handling latency.",
            ),
            "streaming.handle_latency_ms_avg": MetricPoint(
                kind=MetricKind.GAUGE,
                value=snap.coordinator_handle_latency_ms_avg,
                unit="ms",
                description="Rolling average coordinator handling latency.",
            ),
        }
        if snap.kafka_lag_last is not None:
            metrics["streaming.kafka_lag_last"] = MetricPoint(
                kind=MetricKind.GAUGE,
                value=snap.kafka_lag_last,
                unit="messages",
                description="Last observed Kafka lag.",
            )
        for outcome, value in snap.ingestion_outcome_total.items():
            metrics[f"streaming.ingestion_outcome_total.{outcome.lower()}"] = MetricPoint(
                kind=MetricKind.COUNTER,
                value=value,
                unit="messages",
                description="Ingestion outcomes by status.",
                labels={"status": outcome},
            )
        return metrics


@dataclass(slots=True)
class PersistenceMetricsProvider:
    collector: "DBAdapterMetrics"

    def collect_metrics(self) -> dict[str, MetricPoint]:
        return {
            "db.event_append_errors_total": MetricPoint(
                kind=MetricKind.COUNTER,
                value=self.collector.db_event_append_errors_total,
                unit="errors",
                description="Total DB append errors.",
            ),
            "db.query_errors_total": MetricPoint(
                kind=MetricKind.COUNTER,
                value=self.collector.db_query_errors_total,
                unit="errors",
                description="Total DB query errors.",
            ),
            "db.event_append_latency_ms": _latency_point(
                self.collector.db_event_append_latency_ms,
                description="DB event append latency aggregate.",
            ),
            "db.snapshot_save_latency_ms": _latency_point(
                self.collector.db_snapshot_save_latency_ms,
                description="DB snapshot save latency aggregate.",
            ),
            "db.snapshot_load_latency_ms": _latency_point(
                self.collector.db_snapshot_load_latency_ms,
                description="DB snapshot load latency aggregate.",
            ),
        }


def _latency_point(latency: object, *, description: str) -> MetricPoint:
    count = int(getattr(latency, "count", 0))
    total = float(getattr(latency, "total_ms", 0.0))
    min_ms = float(getattr(latency, "min_ms", 0.0)) if count else 0.0
    max_ms = float(getattr(latency, "max_ms", 0.0)) if count else 0.0
    avg_ms = (total / count) if count else 0.0
    return MetricPoint(
        kind=MetricKind.HISTOGRAM,
        value={
            "count": count,
            "min_ms": min_ms,
            "max_ms": max_ms,
            "avg_ms": avg_ms,
            "total_ms": total,
        },
        unit="ms",
        description=description,
    )


@dataclass(slots=True)
class ObservabilityRegistry:
    node_id: str | None = None
    providers: list[MetricsProvider] = field(default_factory=list)

    def register(self, provider: MetricsProvider) -> None:
        self.providers.append(provider)

    def collect_snapshot(self, mode: str) -> MetricsSnapshot:
        collector = SnapshotCollector(tuple(self.providers), node_id=self.node_id)
        return collector.collect(mode=mode)
