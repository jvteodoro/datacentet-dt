from __future__ import annotations

from dataclasses import asdict

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.observability.registry import DomainMetricsProvider, ObservabilityRegistry


def test_metrics_collection_is_observational_only() -> None:
    twin = DataCenterTwin()

    registry = ObservabilityRegistry(node_id="test-node")
    registry.register(DomainMetricsProvider(twin.metrics))

    events = [
        DomainEvent(timestamp=1, type="Tick", payload={"delta_time": 0.1}),
        DomainEvent(timestamp=2, type="Tick", payload={"delta_time": 0.2}),
        DomainEvent(timestamp=3, type="Tick", payload={"delta_time": 0.3}),
    ]

    for event in events:
        twin.ingest_event(event)
        state_before = asdict(twin.get_snapshot())
        log_before = twin.event_log

        snapshot = registry.collect_snapshot("LIVE")

        assert snapshot.mode == "LIVE"
        assert asdict(twin.get_snapshot()) == state_before
        assert twin.event_log == log_before
