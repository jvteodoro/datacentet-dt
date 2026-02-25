from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.optimization.engine import OptimizationEngine
from digital_twin.optimization.registry import StrategyRegistry
from digital_twin.optimization.strategies.baseline import BaselineOptimizationStrategy


def _snapshot(backlog: float, version: int = 10) -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=version,
        event_counter=version,
        total_nodes=0,
        total_links=0,
        total_servers=0,
        active_flows_count=0,
        total_active_workloads=0,
        total_backlog=backlog,
        total_active_links=1,
        total_active_servers=0,
        aggregate_cpu_usage=0.0,
        aggregate_memory_usage=0.0,
        link_backlog=(),
        cpu_usage=(),
        memory_usage=(),
        topology_node_ids=(),
        topology_adjacency=(),
        topology_link_capacity=(),
        topology_links=(),
        compute_server_ids=(),
        compute_cpu_capacity=(),
        compute_memory_capacity=(),
        active_flows=(),
        server_workload_count=(),
        active_workloads=(),
        active_link_indices=(),
        active_server_indices=(),
    )


def test_same_inputs_produce_identical_actions_in_identical_order() -> None:
    registry = StrategyRegistry()
    registry.register(BaselineOptimizationStrategy(backlog_threshold=5.0))
    engine = OptimizationEngine(registry)
    snapshot = _snapshot(backlog=15.0, version=3)

    first = engine.on_snapshot(snapshot, params={}).actions
    second = engine.on_snapshot(snapshot, params={}).actions

    assert first == second
    assert tuple(action.action_id for action in first) == tuple(action.action_id for action in second)
