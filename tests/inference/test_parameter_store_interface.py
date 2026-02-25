from collections.abc import Iterable

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.parameter import ParameterVector
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.store import ParameterStore
from digital_twin.inference.strategies.moving_average import MovingAverageStrategy


class _InMemoryParameterStore(ParameterStore):
    def __init__(self) -> None:
        self.values: list[ParameterVector] = []

    def append(self, parameter_vector: ParameterVector) -> None:
        self.values.append(parameter_vector)

    def load_all(self) -> Iterable[ParameterVector]:
        return tuple(self.values)


def test_engine_appends_validated_parameters_when_store_is_configured() -> None:
    registry = StrategyRegistry()
    registry.register(MovingAverageStrategy(metrics=("active_link_count",)))
    store = _InMemoryParameterStore()
    engine = InferenceEngine(registry, parameter_store=store)

    snapshot = TwinSnapshot(
        version_counter=1,
        event_counter=1,
        total_nodes=0,
        total_links=0,
        total_servers=0,
        active_flows_count=0,
        total_active_workloads=0,
        total_backlog=0.0,
        total_active_links=0,
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

    engine.on_snapshot(snapshot)
    snapshot_2 = TwinSnapshot(
        version_counter=2,
        event_counter=2,
        total_nodes=0,
        total_links=0,
        total_servers=0,
        active_flows_count=0,
        total_active_workloads=0,
        total_backlog=0.0,
        total_active_links=0,
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

    engine.on_snapshot(snapshot_2)

    assert len(store.values) == 2
    assert store.values[-1].timestamp == snapshot_2.version_counter
