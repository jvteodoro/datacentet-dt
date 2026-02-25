from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.strategies.moving_average import MovingAverageStrategy


def _snapshot(version: int, active_links: int, cpu_usage: tuple[float, ...], active_servers: tuple[int, ...], backlog: tuple[float, ...], active_link_indices: tuple[int, ...]) -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=version,
        event_counter=version,
        total_nodes=0,
        total_links=len(backlog),
        total_servers=len(cpu_usage),
        active_flows_count=0,
        total_active_workloads=0,
        total_backlog=sum(backlog),
        total_active_links=active_links,
        total_active_servers=len(active_servers),
        aggregate_cpu_usage=sum(cpu_usage),
        aggregate_memory_usage=0.0,
        link_backlog=backlog,
        cpu_usage=cpu_usage,
        memory_usage=tuple(0.0 for _ in cpu_usage),
        topology_node_ids=(),
        topology_adjacency=(),
        topology_link_capacity=(),
        topology_links=(),
        compute_server_ids=tuple(f"S{i}" for i in range(len(cpu_usage))),
        compute_cpu_capacity=tuple(1.0 for _ in cpu_usage),
        compute_memory_capacity=tuple(1.0 for _ in cpu_usage),
        active_flows=(),
        server_workload_count=tuple(0 for _ in cpu_usage),
        active_workloads=(),
        active_link_indices=active_link_indices,
        active_server_indices=active_servers,
    )


def test_moving_average_uses_incremental_online_formula() -> None:
    strategy = MovingAverageStrategy(metrics=("active_link_count", "cpu_usage_per_server", "backlog"))
    strategy.initialize(_snapshot(0, 0, (0.0,), (), (0.0,), ()))

    s1 = _snapshot(1, 2, (4.0, 2.0), (0, 1), (5.0, 3.0), (0, 1))
    s2 = _snapshot(2, 2, (8.0, 2.0), (0, 1), (9.0, 3.0), (0, 1))

    p1 = strategy.update(s1).parameter_vector.values
    p2 = strategy.update(s2).parameter_vector.values

    assert p1 == (2.0, 3.0, 4.0)
    assert p2 == (2.0, 4.0, 5.0)
