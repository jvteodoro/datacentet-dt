from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.optimization.engine import OptimizationEngine, OptimizationMode
from digital_twin.optimization.registry import StrategyRegistry
from digital_twin.optimization.strategies.baseline import BaselineOptimizationStrategy


def _snapshot(version: int, backlog: float) -> TwinSnapshot:
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


def _engine(mode: OptimizationMode) -> OptimizationEngine:
    registry = StrategyRegistry()
    registry.register(BaselineOptimizationStrategy(backlog_threshold=5.0))
    return OptimizationEngine(registry, mode=mode)


def test_mode_live_and_replay_emit_identical_actions() -> None:
    live = _engine(OptimizationMode.LIVE)
    replay = _engine(OptimizationMode.REPLAY)
    snapshot = _snapshot(version=7, backlog=20.0)

    assert live.on_snapshot(snapshot, params={}).actions == replay.on_snapshot(snapshot, params={}).actions


def test_mode_disabled_emits_no_actions() -> None:
    disabled = _engine(OptimizationMode.DISABLED)
    snapshot = _snapshot(version=7, backlog=20.0)

    result = disabled.on_snapshot(snapshot, params={})

    assert result.actions == ()
    assert disabled.get_latest_actions() == ()
