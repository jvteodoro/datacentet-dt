"""Unified observability metrics pipeline."""

from .cache import MetricsSnapshotCache
from .clock import Clock, DefaultClock
from .config import OBS_HIST_BINS_BACKLOG, OBS_HIST_BINS_CPU, OBS_HIST_BINS_MEM, OBS_TOPK_DEFAULT, OBS_TOPK_HARD_MAX
from .model import Histogram, MetricKind, MetricPoint, MetricsSnapshot, TopKEntry
from .registry import (
    DomainMetricsProvider,
    ObservabilityRegistry,
    PersistenceMetricsProvider,
    StreamingMetricsProvider,
    NetworkInsightProvider,
    ComputeInsightProvider,
)
from .snapshot import histogram_aggregates, snapshot_schema, stream_aggregates, topk_aggregates

__all__ = [
    "Clock",
    "DefaultClock",
    "MetricKind",
    "MetricPoint",
    "MetricsSnapshot",
    "MetricsSnapshotCache",
    "TopKEntry",
    "Histogram",
    "OBS_TOPK_DEFAULT",
    "OBS_TOPK_HARD_MAX",
    "OBS_HIST_BINS_BACKLOG",
    "OBS_HIST_BINS_CPU",
    "OBS_HIST_BINS_MEM",
    "ObservabilityRegistry",
    "DomainMetricsProvider",
    "StreamingMetricsProvider",
    "PersistenceMetricsProvider",
    "NetworkInsightProvider",
    "ComputeInsightProvider",
    "snapshot_schema",
    "stream_aggregates",
    "topk_aggregates",
    "histogram_aggregates",
]
