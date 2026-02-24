from dataclasses import dataclass


@dataclass(slots=True)
class MetricsCollector:
    """O(1) ingestion metrics."""

    events_processed_total: int = 0
    last_event_latency_ns: int = 0
    total_event_latency_ns: int = 0

    def record_ingestion_latency(self, latency_ns: int) -> None:
        self.events_processed_total += 1
        self.last_event_latency_ns = latency_ns
        self.total_event_latency_ns += latency_ns
