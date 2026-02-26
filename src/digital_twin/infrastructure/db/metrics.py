from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class _LatencyStats:
    count: int = 0
    total_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0

    def record(self, value_ms: float) -> None:
        self.count += 1
        self.total_ms += value_ms
        if self.count == 1:
            self.min_ms = value_ms
            self.max_ms = value_ms
            return
        self.min_ms = min(self.min_ms, value_ms)
        self.max_ms = max(self.max_ms, value_ms)


@dataclass(slots=True)
class DBAdapterMetrics:
    """Observational DB adapter metrics (no domain-state coupling)."""

    db_event_append_latency_ms: _LatencyStats = field(default_factory=_LatencyStats)
    db_snapshot_save_latency_ms: _LatencyStats = field(default_factory=_LatencyStats)
    db_snapshot_load_latency_ms: _LatencyStats = field(default_factory=_LatencyStats)
    db_event_append_errors_total: int = 0
    db_query_errors_total: int = 0

    def record_event_append_latency(self, value_ms: float) -> None:
        self.db_event_append_latency_ms.record(value_ms)

    def record_snapshot_save_latency(self, value_ms: float) -> None:
        self.db_snapshot_save_latency_ms.record(value_ms)

    def record_snapshot_load_latency(self, value_ms: float) -> None:
        self.db_snapshot_load_latency_ms.record(value_ms)

    def record_event_append_error(self) -> None:
        self.db_event_append_errors_total += 1

    def record_query_error(self) -> None:
        self.db_query_errors_total += 1
