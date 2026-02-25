from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.inference.engine import InferenceEngine, InferenceMode
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.strategies.moving_average import MovingAverageStrategy


def _events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
        DomainEvent(timestamp=4, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 12.0, "memory_capacity": 12.0}),
        DomainEvent(
            timestamp=5,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 2.0, "size": 20.0},
        ),
        DomainEvent(
            timestamp=6,
            type="WorkloadStarted",
            payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 2.0, "memory_demand": 2.0, "size": 5.0, "cpu_usage_rate": 1.0},
        ),
        DomainEvent(timestamp=7, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=8, type="Tick", payload={"delta_time": 1.0}),
    ]


def _engine(mode: InferenceMode) -> InferenceEngine:
    registry = StrategyRegistry()
    registry.register(MovingAverageStrategy())
    return InferenceEngine(registry, mode=mode)


def test_replay_mode_produces_identical_final_parameters() -> None:
    live_twin = DataCenterTwin()
    replay_twin = DataCenterTwin()

    live_engine = _engine(InferenceMode.LIVE)
    replay_engine = _engine(InferenceMode.REPLAY)

    events = _events()
    for event in events:
        live_twin.ingest_event(event)
        live_engine.on_snapshot(live_twin.get_snapshot())

    for event in events:
        replay_twin.ingest_event(event)
        replay_engine.on_snapshot(replay_twin.get_snapshot())

    assert live_engine.get_parameters() == replay_engine.get_parameters()


def test_disabled_mode_does_not_mutate_inference_state() -> None:
    twin = DataCenterTwin()
    engine = _engine(InferenceMode.DISABLED)

    for event in _events():
        twin.ingest_event(event)
        engine.on_snapshot(twin.get_snapshot())

    assert engine.get_parameters() == {}
