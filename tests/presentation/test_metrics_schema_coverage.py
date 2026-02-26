from __future__ import annotations

import json
import threading
import urllib.request

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.observability.registry import ComputeInsightProvider, NetworkInsightProvider, ObservabilityRegistry
from digital_twin.presentation.metrics_api import create_metrics_api_server


def _snapshot() -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=1,
        event_counter=1,
        total_nodes=2,
        total_links=2,
        total_servers=2,
        active_flows_count=1,
        total_active_workloads=2,
        total_backlog=15.0,
        total_active_links=1,
        total_active_servers=2,
        aggregate_cpu_usage=55.0,
        aggregate_memory_usage=90.0,
        link_backlog=(5.0, 10.0),
        cpu_usage=(35.0, 20.0),
        memory_usage=(40.0, 50.0),
        topology_node_ids=("a", "b"),
        topology_adjacency=((1,), ()),
        topology_link_capacity=(100.0, 100.0),
        topology_links=((0, 1, 0), (1, 0, 1)),
        compute_server_ids=("srv-a", "srv-b"),
        compute_cpu_capacity=(100.0, 100.0),
        compute_memory_capacity=(256.0, 256.0),
        active_flows=(),
        server_workload_count=(1, 1),
        active_workloads=(),
        active_link_indices=(0,),
        active_server_indices=(0, 1),
    )


def _get_json(url: str) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=3) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def test_metrics_schema_includes_scalar_topk_and_histograms() -> None:
    snapshot = _snapshot()
    registry = ObservabilityRegistry(node_id="node-schema")
    registry.register(NetworkInsightProvider(snapshot_reader=lambda: snapshot))
    registry.register(ComputeInsightProvider(snapshot_reader=lambda: snapshot))

    server = create_metrics_api_server(host="127.0.0.1", port=0, registry=registry, mode="LIVE")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        schema = _get_json(f"{base}/metrics/schema")

        names = {item["name"] for item in schema["scalar_metrics"]}
        assert "net.backlog.total" in names
        assert "compute.cpu_usage.total" in names

        categories = {item["category"] for item in schema["topk"]}
        assert "top.links.by_backlog" in categories
        assert "top.servers.by_cpu" in categories

        hists = {item["name"] for item in schema["histograms"]}
        assert "hist.net.backlog" in hists
        assert "hist.compute.cpu_usage" in hists
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
