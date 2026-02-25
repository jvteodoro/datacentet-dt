from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.strategies.moving_average import MovingAverageStrategy


def _events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
        DomainEvent(timestamp=4, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 10.0, "memory_capacity": 10.0}),
        DomainEvent(
            timestamp=5,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 3.0, "size": 30.0},
        ),
        DomainEvent(
            timestamp=6,
            type="WorkloadStarted",
            payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 2.0, "memory_demand": 2.0, "size": 10.0, "cpu_usage_rate": 1.0},
        ),
        DomainEvent(timestamp=7, type="Tick", payload={"delta_time": 1.0}),
    ]


def _build_engine() -> InferenceEngine:
    registry = StrategyRegistry()
    registry.register(MovingAverageStrategy())
    return InferenceEngine(registry)


def test_moving_average_is_deterministic_under_replay() -> None:
    twin_1 = DataCenterTwin()
    twin_2 = DataCenterTwin()
    engine_1 = _build_engine()
    engine_2 = _build_engine()

    for event in _events():
        twin_1.ingest_event(event)
        twin_2.ingest_event(event)
        engine_1.on_snapshot(twin_1.get_snapshot())
        engine_2.on_snapshot(twin_2.get_snapshot())

    assert engine_1.get_parameters() == engine_2.get_parameters()
