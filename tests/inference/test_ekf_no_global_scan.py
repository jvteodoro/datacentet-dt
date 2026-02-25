from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.strategies.ekf import EKFStrategy


class _ForbiddenTuple(tuple):
    def __iter__(self):  # type: ignore[override]
        raise AssertionError("global scan iteration is forbidden")



def test_ekf_update_uses_aggregated_snapshot_fields_only() -> None:
    strategy = EKFStrategy()
    snapshot = TwinSnapshot(
        version_counter=5,
        event_counter=5,
        total_nodes=0,
        total_links=3,
        total_servers=3,
        active_flows_count=0,
        total_active_workloads=2,
        total_backlog=10.0,
        total_active_links=2,
        total_active_servers=2,
        aggregate_cpu_usage=5.0,
        aggregate_memory_usage=0.0,
        link_backlog=_ForbiddenTuple((100.0, 200.0, 300.0)),
        cpu_usage=_ForbiddenTuple((1.0, 2.0, 3.0)),
        memory_usage=_ForbiddenTuple((0.0, 0.0, 0.0)),
        topology_node_ids=(),
        topology_adjacency=(),
        topology_link_capacity=(),
        topology_links=(),
        compute_server_ids=("S1", "S2", "S3"),
        compute_cpu_capacity=(1.0, 1.0, 1.0),
        compute_memory_capacity=(1.0, 1.0, 1.0),
        active_flows=(),
        server_workload_count=(0, 0, 0),
        active_workloads=(),
        active_link_indices=(0, 1),
        active_server_indices=(0, 1),
    )

    strategy.initialize(snapshot)
    result = strategy.update(snapshot)

    assert len(result.parameter_vector.values) == 2
    assert result.metadata["active_workloads"] == 2.0
    assert result.metadata["active_links"] == 2.0
