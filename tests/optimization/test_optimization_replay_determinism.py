from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.optimization.engine import OptimizationEngine, OptimizationMode
from digital_twin.optimization.registry import StrategyRegistry
from digital_twin.optimization.strategies.baseline import BaselineOptimizationStrategy


def _events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
        DomainEvent(
            timestamp=4,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 6.0, "size": 10.0},
        ),
    ]


def _engine(mode: OptimizationMode) -> OptimizationEngine:
    registry = StrategyRegistry()
    registry.register(BaselineOptimizationStrategy(backlog_threshold=2.0))
    return OptimizationEngine(registry, mode=mode)


def test_replay_mode_reproduces_identical_action_event_stream() -> None:
    events = _events()
    live_twin = DataCenterTwin()
    replay_twin = DataCenterTwin()

    live_engine = _engine(OptimizationMode.LIVE)
    replay_engine = _engine(OptimizationMode.REPLAY)

    live_stream: list[tuple[DomainEvent, ...]] = []
    replay_stream: list[tuple[DomainEvent, ...]] = []

    for event in events:
        live_twin.ingest_event(event)
        live_engine.on_snapshot(live_twin.get_snapshot(), params={})
        live_stream.append(live_engine.as_domain_events())

    for event in events:
        replay_twin.ingest_event(event)
        replay_engine.on_snapshot(replay_twin.get_snapshot(), params={})
        replay_stream.append(replay_engine.as_domain_events())

    assert live_stream == replay_stream
