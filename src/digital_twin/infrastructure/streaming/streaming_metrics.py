from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True, slots=True)
class StreamingMetricsSnapshot:
    streams_active_gauge: int
    streams_evicted_total: int
    streams_evicted_ttl_total: int
    streams_evicted_capacity_total: int
    ingestion_outcome_total: dict[str, int]
    coordinator_handle_latency_ms_avg: float
    coordinator_handle_latency_ms_last: float
    kafka_lag_last: int | None


class StreamingMetricsCollector:
    """Observational side-channel metrics for streaming coordinator/consumer."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._streams_active_gauge = 0
        self._streams_evicted_total = 0
        self._streams_evicted_ttl_total = 0
        self._streams_evicted_capacity_total = 0
        self._ingestion_outcome_total: dict[str, int] = {
            "APPLIED": 0,
            "DUPLICATE": 0,
            "DLQ": 0,
            "VERSION_CONFLICT": 0,
        }
        self._latency_samples_ms: deque[float] = deque(maxlen=256)
        self._coordinator_handle_latency_ms_last = 0.0
        self._kafka_lag_last: int | None = None

    def set_streams_active_gauge(self, value: int) -> None:
        with self._lock:
            self._streams_active_gauge = max(0, int(value))

    def record_eviction(self, *, reason: str) -> None:
        with self._lock:
            self._streams_evicted_total += 1
            if reason == "TTL":
                self._streams_evicted_ttl_total += 1
            elif reason == "CAPACITY":
                self._streams_evicted_capacity_total += 1

    def record_outcome(self, *, status: str) -> None:
        with self._lock:
            self._ingestion_outcome_total[status] = self._ingestion_outcome_total.get(status, 0) + 1

    def record_handle_latency_ms(self, latency_ms: float) -> None:
        with self._lock:
            v = float(latency_ms)
            self._coordinator_handle_latency_ms_last = v
            self._latency_samples_ms.append(v)

    def set_kafka_lag_last(self, value: int | None) -> None:
        with self._lock:
            self._kafka_lag_last = None if value is None else int(value)

    def snapshot(self) -> StreamingMetricsSnapshot:
        with self._lock:
            avg = (sum(self._latency_samples_ms) / len(self._latency_samples_ms)) if self._latency_samples_ms else 0.0
            return StreamingMetricsSnapshot(
                streams_active_gauge=self._streams_active_gauge,
                streams_evicted_total=self._streams_evicted_total,
                streams_evicted_ttl_total=self._streams_evicted_ttl_total,
                streams_evicted_capacity_total=self._streams_evicted_capacity_total,
                ingestion_outcome_total=dict(self._ingestion_outcome_total),
                coordinator_handle_latency_ms_avg=avg,
                coordinator_handle_latency_ms_last=self._coordinator_handle_latency_ms_last,
                kafka_lag_last=self._kafka_lag_last,
            )
