from __future__ import annotations

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.observability.config import OBS_HIST_BINS_BACKLOG, OBS_HIST_BINS_CPU, OBS_HIST_BINS_MEM, OBS_TOPK_HARD_MAX
from digital_twin.observability.registry import ComputeInsightProvider, NetworkInsightProvider


def _snapshot() -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=1,
        event_counter=1,
        total_nodes=3,
        total_links=4,
        total_servers=3,
        active_flows_count=3,
        total_active_workloads=4,
        total_backlog=57.0,
        total_active_links=3,
        total_active_servers=3,
        aggregate_cpu_usage=90.0,
        aggregate_memory_usage=160.0,
        link_backlog=(11.0, 11.0, 22.0, 13.0),
        cpu_usage=(20.0, 20.0, 50.0),
        memory_usage=(40.0, 70.0, 50.0),
        topology_node_ids=("n1", "n2", "n3"),
        topology_adjacency=((1,), (2,), ()),
        topology_link_capacity=(100.0, 100.0, 100.0, 100.0),
        topology_links=((0, 1, 0), (1, 2, 1), (0, 2, 2), (2, 1, 3)),
        compute_server_ids=("srv-c", "srv-a", "srv-b"),
        compute_cpu_capacity=(100.0, 100.0, 100.0),
        compute_memory_capacity=(256.0, 256.0, 256.0),
        active_flows=(),
        server_workload_count=(1, 2, 1),
        active_workloads=(),
        active_link_indices=(0, 1, 2),
        active_server_indices=(0, 1, 2),
    )


def test_topk_ordering_tie_break_and_cardinality_limits() -> None:
    snapshot = _snapshot()
    net = NetworkInsightProvider(snapshot_reader=lambda: snapshot, topk_limit=999)
    compute = ComputeInsightProvider(snapshot_reader=lambda: snapshot, topk_limit=999)

    net_top = net.collect_topk()["top.links.by_backlog"]
    assert len(net_top) <= OBS_TOPK_HARD_MAX
    assert [item.id for item in net_top[:2]] == ["link-2", "link-3"]
    assert [item.id for item in net_top[2:4]] == ["link-0", "link-1"]

    cpu_top = compute.collect_topk()["top.servers.by_cpu"]
    assert len(cpu_top) <= OBS_TOPK_HARD_MAX
    assert [item.id for item in cpu_top[:3]] == ["srv-b", "srv-a", "srv-c"]


def test_histograms_use_fixed_bins() -> None:
    snapshot = _snapshot()
    net = NetworkInsightProvider(snapshot_reader=lambda: snapshot)
    compute = ComputeInsightProvider(snapshot_reader=lambda: snapshot)

    net_hist = net.collect_histograms()["hist.net.backlog"]
    assert net_hist.bin_edges == OBS_HIST_BINS_BACKLOG
    assert len(net_hist.counts) == len(OBS_HIST_BINS_BACKLOG) - 1

    cpu_hist = compute.collect_histograms()["hist.compute.cpu_usage"]
    mem_hist = compute.collect_histograms()["hist.compute.mem_usage"]
    assert cpu_hist.bin_edges == OBS_HIST_BINS_CPU
    assert mem_hist.bin_edges == OBS_HIST_BINS_MEM


def test_always_on_metrics_have_no_forbidden_dimensions() -> None:
    snapshot = _snapshot()
    metrics = {}
    metrics.update(NetworkInsightProvider(snapshot_reader=lambda: snapshot).collect_metrics())
    metrics.update(ComputeInsightProvider(snapshot_reader=lambda: snapshot).collect_metrics())

    forbidden = ("flow_id", "workload_id")
    for metric_name, point in metrics.items():
        assert all(token not in metric_name for token in forbidden)
        assert all(label not in forbidden for label in point.labels)
