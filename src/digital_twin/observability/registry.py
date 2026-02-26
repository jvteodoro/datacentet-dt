from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

from digital_twin.domain.metrics import MetricsCollector
from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.infrastructure.streaming.streaming_metrics import StreamingMetricsCollector

from .collector import MetricsProvider, SnapshotCollector
from .config import OBS_HIST_BINS_BACKLOG, OBS_HIST_BINS_CPU, OBS_HIST_BINS_MEM, OBS_TOPK_DEFAULT, OBS_TOPK_HARD_MAX
from .model import Histogram, MetricKind, MetricPoint, MetricsSnapshot, TopKEntry

if TYPE_CHECKING:
    from digital_twin.infrastructure.db.metrics import DBAdapterMetrics


@dataclass(slots=True)
class DomainMetricsProvider:
    collector: MetricsCollector

    def collect_metrics(self) -> dict[str, MetricPoint]:
        total = self.collector.events_processed_total
        avg_ns = (self.collector.total_event_latency_ns / total) if total else 0.0
        return {
            "domain.events_processed_total": MetricPoint(kind=MetricKind.COUNTER, value=total, unit="events", description="Total ingested domain events."),
            "domain.ingestion_latency_ns_last": MetricPoint(kind=MetricKind.GAUGE, value=self.collector.last_event_latency_ns, unit="ns", description="Most recent ingestion latency measured at boundary."),
            "domain.ingestion_latency_ns_avg": MetricPoint(kind=MetricKind.GAUGE, value=avg_ns, unit="ns", description="Average ingestion latency measured at boundary."),
        }


@dataclass(slots=True)
class StreamingMetricsProvider:
    collector: StreamingMetricsCollector

    def collect_metrics(self) -> dict[str, MetricPoint]:
        snap = self.collector.snapshot()
        metrics: dict[str, MetricPoint] = {
            "streaming.streams_active": MetricPoint(kind=MetricKind.GAUGE, value=snap.streams_active_gauge, unit="streams", description="Active stream coordinators in memory."),
            "streaming.evictions_total": MetricPoint(kind=MetricKind.COUNTER, value=snap.streams_evicted_total, unit="streams", description="Total stream evictions."),
            "streaming.evictions_ttl_total": MetricPoint(kind=MetricKind.COUNTER, value=snap.streams_evicted_ttl_total, unit="streams", description="Total stream evictions by TTL."),
            "streaming.evictions_capacity_total": MetricPoint(kind=MetricKind.COUNTER, value=snap.streams_evicted_capacity_total, unit="streams", description="Total stream evictions by capacity."),
            "streaming.handle_latency_ms_last": MetricPoint(kind=MetricKind.GAUGE, value=snap.coordinator_handle_latency_ms_last, unit="ms", description="Last coordinator handling latency."),
            "streaming.handle_latency_ms_avg": MetricPoint(kind=MetricKind.GAUGE, value=snap.coordinator_handle_latency_ms_avg, unit="ms", description="Rolling average coordinator handling latency."),
        }
        if snap.kafka_lag_last is not None:
            metrics["streaming.kafka_lag_last"] = MetricPoint(kind=MetricKind.GAUGE, value=snap.kafka_lag_last, unit="messages", description="Last observed Kafka lag.")
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
            "db.event_append_errors_total": MetricPoint(kind=MetricKind.COUNTER, value=self.collector.db_event_append_errors_total, unit="errors", description="Total DB append errors."),
            "db.query_errors_total": MetricPoint(kind=MetricKind.COUNTER, value=self.collector.db_query_errors_total, unit="errors", description="Total DB query errors."),
            "db.event_append_latency_ms": _latency_point(self.collector.db_event_append_latency_ms, description="DB event append latency aggregate."),
            "db.snapshot_save_latency_ms": _latency_point(self.collector.db_snapshot_save_latency_ms, description="DB snapshot save latency aggregate."),
            "db.snapshot_load_latency_ms": _latency_point(self.collector.db_snapshot_load_latency_ms, description="DB snapshot load latency aggregate."),
        }


@dataclass(slots=True)
class NetworkInsightProvider:
    snapshot_reader: Callable[[], TwinSnapshot]
    topk_limit: int = OBS_TOPK_DEFAULT

    def __post_init__(self) -> None:
        self.topk_limit = min(max(1, int(self.topk_limit)), OBS_TOPK_HARD_MAX)

    def collect_metrics(self) -> dict[str, MetricPoint]:
        snapshot = self.snapshot_reader()
        return {
            "net.active_flows.count": MetricPoint(kind=MetricKind.GAUGE, value=snapshot.active_flows_count, unit="flows", description="Active network flows."),
            "net.backlog.total": MetricPoint(kind=MetricKind.GAUGE, value=snapshot.total_backlog, unit="packets", description="Total network backlog."),
            "net.backlog.max": MetricPoint(kind=MetricKind.GAUGE, value=max(snapshot.link_backlog, default=0.0), unit="packets", description="Maximum backlog across links."),
        }

    def collect_topk(self) -> dict[str, tuple[TopKEntry, ...]]:
        snapshot = self.snapshot_reader()
        ranked = sorted(
            ((f"link-{idx}", float(backlog)) for idx, backlog in enumerate(snapshot.link_backlog)),
            key=lambda item: (-item[1], item[0]),
        )
        entries = tuple(TopKEntry(id=link_id, value=value) for link_id, value in ranked[: self.topk_limit])
        return {"top.links.by_backlog": entries}

    def collect_histograms(self) -> dict[str, Histogram]:
        snapshot = self.snapshot_reader()
        return {"hist.net.backlog": _histogram(snapshot.link_backlog, OBS_HIST_BINS_BACKLOG)}


@dataclass(slots=True)
class ComputeInsightProvider:
    snapshot_reader: Callable[[], TwinSnapshot]
    topk_limit: int = OBS_TOPK_DEFAULT

    def __post_init__(self) -> None:
        self.topk_limit = min(max(1, int(self.topk_limit)), OBS_TOPK_HARD_MAX)

    def collect_metrics(self) -> dict[str, MetricPoint]:
        snapshot = self.snapshot_reader()
        return {
            "compute.active_workloads.count": MetricPoint(kind=MetricKind.GAUGE, value=snapshot.total_active_workloads, unit="workloads", description="Total active workloads."),
            "compute.cpu_usage.total": MetricPoint(kind=MetricKind.GAUGE, value=snapshot.aggregate_cpu_usage, unit="cpu", description="Total compute CPU usage."),
            "compute.cpu_usage.max": MetricPoint(kind=MetricKind.GAUGE, value=max(snapshot.cpu_usage, default=0.0), unit="cpu", description="Maximum CPU usage on a server."),
            "compute.mem_usage.total": MetricPoint(kind=MetricKind.GAUGE, value=snapshot.aggregate_memory_usage, unit="memory", description="Total compute memory usage."),
            "compute.mem_usage.max": MetricPoint(kind=MetricKind.GAUGE, value=max(snapshot.memory_usage, default=0.0), unit="memory", description="Maximum memory usage on a server."),
        }

    def collect_topk(self) -> dict[str, tuple[TopKEntry, ...]]:
        snapshot = self.snapshot_reader()
        cpu_ranked = sorted(((server_id, float(snapshot.cpu_usage[idx])) for idx, server_id in enumerate(snapshot.compute_server_ids)), key=lambda item: (-item[1], item[0]))
        mem_ranked = sorted(((server_id, float(snapshot.memory_usage[idx])) for idx, server_id in enumerate(snapshot.compute_server_ids)), key=lambda item: (-item[1], item[0]))
        return {
            "top.servers.by_cpu": tuple(TopKEntry(id=server_id, value=value) for server_id, value in cpu_ranked[: self.topk_limit]),
            "top.servers.by_mem": tuple(TopKEntry(id=server_id, value=value) for server_id, value in mem_ranked[: self.topk_limit]),
        }

    def collect_histograms(self) -> dict[str, Histogram]:
        snapshot = self.snapshot_reader()
        return {
            "hist.compute.cpu_usage": _histogram(snapshot.cpu_usage, OBS_HIST_BINS_CPU),
            "hist.compute.mem_usage": _histogram(snapshot.memory_usage, OBS_HIST_BINS_MEM),
        }


def _latency_point(latency: object, *, description: str) -> MetricPoint:
    count = int(getattr(latency, "count", 0))
    total = float(getattr(latency, "total_ms", 0.0))
    min_ms = float(getattr(latency, "min_ms", 0.0)) if count else 0.0
    max_ms = float(getattr(latency, "max_ms", 0.0)) if count else 0.0
    avg_ms = (total / count) if count else 0.0
    return MetricPoint(
        kind=MetricKind.HISTOGRAM,
        value={"count": count, "min_ms": min_ms, "max_ms": max_ms, "avg_ms": avg_ms, "total_ms": total},
        unit="ms",
        description=description,
    )


def _histogram(values: tuple[float, ...], edges: tuple[float, ...]) -> Histogram:
    counts = [0 for _ in range(len(edges) - 1)]
    for value in values:
        assigned = False
        for idx in range(len(edges) - 1):
            low = edges[idx]
            high = edges[idx + 1]
            inclusive_high = idx == len(edges) - 2
            if (value >= low and value < high) or (inclusive_high and value == high):
                counts[idx] += 1
                assigned = True
                break
        if not assigned:
            if value < edges[0]:
                counts[0] += 1
            else:
                counts[-1] += 1
    return Histogram(bin_edges=edges, counts=tuple(counts))


@dataclass(slots=True)
class ObservabilityRegistry:
    node_id: str | None = None
    providers: list[MetricsProvider] = field(default_factory=list)

    def register(self, provider: MetricsProvider) -> None:
        self.providers.append(provider)

    def collect_snapshot(self, mode: str) -> MetricsSnapshot:
        collector = SnapshotCollector(tuple(self.providers), node_id=self.node_id)
        return collector.collect(mode=mode)
