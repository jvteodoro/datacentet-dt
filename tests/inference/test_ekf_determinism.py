from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.strategies.ekf import EKFStrategy


def _events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 12.0}),
        DomainEvent(timestamp=4, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 10.0, "memory_capacity": 10.0}),
        DomainEvent(timestamp=5, type="AddServer", payload={"server_id": "S2", "cpu_capacity": 10.0, "memory_capacity": 10.0}),
        DomainEvent(
            timestamp=6,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 3.0, "size": 20.0},
        ),
        DomainEvent(
            timestamp=7,
            type="WorkloadStarted",
            payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 2.0, "memory_demand": 2.0, "size": 8.0, "cpu_usage_rate": 1.2},
        ),
        DomainEvent(timestamp=8, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=9, type="Tick", payload={"delta_time": 1.0}),
    ]


def _engine() -> InferenceEngine:
    registry = StrategyRegistry()
    registry.register(EKFStrategy())
    return InferenceEngine(registry)


def test_ekf_is_deterministic_for_identical_snapshot_stream() -> None:
    twin_1 = DataCenterTwin()
    twin_2 = DataCenterTwin()
    engine_1 = _engine()
    engine_2 = _engine()

    seq_1 = []
    seq_2 = []
    for event in _events():
        twin_1.ingest_event(event)
        twin_2.ingest_event(event)
        seq_1.append(engine_1.on_snapshot(twin_1.get_snapshot())["ekf"])
        seq_2.append(engine_2.on_snapshot(twin_2.get_snapshot())["ekf"])

    assert seq_1 == seq_2
