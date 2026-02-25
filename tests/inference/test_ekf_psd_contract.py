from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.inference.contracts import validate_parameter_vector
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.strategies.ekf import EKFStrategy


def _events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 20.0}),
        DomainEvent(timestamp=4, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 12.0, "memory_capacity": 12.0}),
        DomainEvent(timestamp=5, type="FlowStarted", payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 5.0, "size": 10.0}),
        DomainEvent(timestamp=6, type="WorkloadStarted", payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 1.5, "memory_demand": 1.0, "size": 4.0, "cpu_usage_rate": 1.0}),
        DomainEvent(timestamp=7, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=8, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=9, type="Tick", payload={"delta_time": 1.0}),
    ]


def test_ekf_covariance_is_psd_for_all_outputs() -> None:
    registry = StrategyRegistry()
    registry.register(EKFStrategy())
    engine = InferenceEngine(registry)
    twin = DataCenterTwin()

    previous_timestamp = None
    for event in _events():
        twin.ingest_event(event)
        vector = engine.on_snapshot(twin.get_snapshot())["ekf"]
        validate_parameter_vector(vector, previous_timestamp=previous_timestamp)
        previous_timestamp = vector.timestamp
