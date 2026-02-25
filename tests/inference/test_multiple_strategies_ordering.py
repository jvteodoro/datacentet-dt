from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.parameter import ParameterVector
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.result import InferenceResult
from digital_twin.inference.strategy import InferenceStrategy


class _RecordingStrategy(InferenceStrategy):
    def __init__(self, strategy_id: str, recorder: list[str]) -> None:
        self._strategy_id = strategy_id
        self._recorder = recorder
        self._vector = ParameterVector(values=(0.0,), covariance=None, timestamp=0, strategy_id=strategy_id)

    def initialize(self, snapshot: TwinSnapshot) -> None:
        self._vector = ParameterVector(values=(0.0,), covariance=None, timestamp=snapshot.version_counter, strategy_id=self._strategy_id)

    def update(self, snapshot: TwinSnapshot) -> InferenceResult:
        self._recorder.append(self._strategy_id)
        self._vector = ParameterVector(values=(float(len(self._recorder)),), covariance=None, timestamp=snapshot.version_counter, strategy_id=self._strategy_id)
        return InferenceResult(parameter_vector=self._vector, metadata={})

    def get_parameters(self) -> ParameterVector:
        return self._vector

    def name(self) -> str:
        return self._strategy_id


def test_engine_executes_registered_strategies_in_sorted_order() -> None:
    recorder: list[str] = []
    registry = StrategyRegistry()
    registry.register(_RecordingStrategy("zeta", recorder))
    registry.register(_RecordingStrategy("alpha", recorder))

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

    engine.on_snapshot(snapshot)

    assert recorder == ["alpha", "zeta"]
