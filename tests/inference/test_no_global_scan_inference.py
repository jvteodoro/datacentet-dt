import pytest

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.strategies.moving_average import MovingAverageStrategy


def test_moving_average_does_not_iterate_full_snapshot_arrays(monkeypatch: pytest.MonkeyPatch) -> None:
    strategy = MovingAverageStrategy(metrics=("active_link_count", "cpu_usage_per_server", "backlog"))

    class _ForbiddenTuple(tuple):
        def __iter__(self):  # type: ignore[override]
            raise AssertionError("global scan iteration is forbidden")

    snapshot = TwinSnapshot(
        version_counter=1,
        event_counter=1,
        total_nodes=0,
        total_links=3,
        total_servers=3,
        active_flows_count=0,
        total_active_workloads=0,
        total_backlog=9.0,
        total_active_links=2,
        total_active_servers=2,
        aggregate_cpu_usage=6.0,
        aggregate_memory_usage=0.0,
        link_backlog=_ForbiddenTuple((100.0, 200.0, 300.0)),
        cpu_usage=_ForbiddenTuple((1.0, 2.0, 3.0)),
        memory_usage=(0.0, 0.0, 0.0),
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

    assert result.parameter_vector.values == (2.0, 3.0, 4.5)
