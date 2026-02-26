from __future__ import annotations

from dataclasses import asdict

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.observability.registry import ComputeInsightProvider, NetworkInsightProvider


def test_insight_providers_are_observational_only() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="Tick", payload={"delta_time": 0.1}))

    snapshot = twin.get_snapshot()
    snapshot_before = asdict(snapshot)
    log_before = twin.event_log

    network = NetworkInsightProvider(snapshot_reader=twin.get_snapshot)
    compute = ComputeInsightProvider(snapshot_reader=twin.get_snapshot)

    network.collect_metrics()
    network.collect_topk()
    network.collect_histograms()
    compute.collect_metrics()
    compute.collect_topk()
    compute.collect_histograms()

    assert asdict(twin.get_snapshot()) == snapshot_before
    assert twin.event_log == log_before
