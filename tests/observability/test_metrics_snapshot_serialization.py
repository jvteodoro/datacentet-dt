from __future__ import annotations

import json

from digital_twin.domain.metrics import MetricsCollector
from digital_twin.observability.registry import DomainMetricsProvider, ObservabilityRegistry


def test_snapshot_json_has_stable_order_and_required_fields() -> None:
    collector = MetricsCollector()
    collector.record_ingestion_latency(11)
    collector.record_ingestion_latency(7)

    registry = ObservabilityRegistry(node_id="node-a")
    registry.register(DomainMetricsProvider(collector))

    snapshot = registry.collect_snapshot("LIVE")
    payload = snapshot.to_json()

    assert payload == snapshot.to_json()
    decoded = json.loads(payload)

    assert set(decoded.keys()) == {"metrics", "mode", "node_id", "timestamp_utc", "produced_at_utc", "snapshot_age_ms"}
    assert decoded["mode"] == "LIVE"
    assert decoded["node_id"] == "node-a"

    metric_names = list(decoded["metrics"].keys())
    assert metric_names == sorted(metric_names)

    for metric in decoded["metrics"].values():
        assert set(metric.keys()) == {"description", "kind", "labels", "unit", "value"}
        assert isinstance(metric["labels"], dict)
