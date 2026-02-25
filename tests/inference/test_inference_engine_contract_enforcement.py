import pytest

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.parameter import ParameterVector
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.result import InferenceResult
from digital_twin.inference.strategy import InferenceStrategy


class _MismatchedStrategy(InferenceStrategy):
    def initialize(self, snapshot: TwinSnapshot) -> None:
        return None

    def update(self, snapshot: TwinSnapshot) -> InferenceResult:
        return InferenceResult(
            parameter_vector=ParameterVector(values=(1.0,), covariance=None, timestamp=snapshot.version_counter, strategy_id="other"),
            metadata={},
        )

    def get_parameters(self) -> ParameterVector:
        return ParameterVector(values=(0.0,), covariance=None, timestamp=0, strategy_id="other")

    def name(self) -> str:
        return "expected"


def test_engine_rejects_strategy_id_mismatch() -> None:
    registry = StrategyRegistry()
    registry.register(_MismatchedStrategy())
    engine = InferenceEngine(registry)

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

    with pytest.raises(ValueError, match="strategy_id"):
        engine.on_snapshot(snapshot)
