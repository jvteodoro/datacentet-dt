from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.strategies.moving_average import MovingAverageStrategy


def test_inference_does_not_mutate_domain_state() -> None:
    twin = DataCenterTwin()
    events = [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 12.0, "memory_capacity": 12.0}),
    ]
    for event in events:
        twin.ingest_event(event)

    state_before = twin.state
    snapshot_before = twin.get_snapshot()

    registry = StrategyRegistry()
    registry.register(MovingAverageStrategy())
    engine = InferenceEngine(registry)

    engine.on_snapshot(snapshot_before)

    assert twin.state == state_before
    assert twin.get_snapshot() == snapshot_before
