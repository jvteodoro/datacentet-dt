from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.optimization.engine import OptimizationEngine
from digital_twin.optimization.registry import StrategyRegistry
from digital_twin.optimization.strategies.baseline import BaselineOptimizationStrategy


def test_optimization_does_not_mutate_domain_state_directly() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}))

    state_before = twin.state
    snapshot_before = twin.get_snapshot()

    registry = StrategyRegistry()
    registry.register(BaselineOptimizationStrategy(backlog_threshold=0.0))
    engine = OptimizationEngine(registry)

    result = engine.on_snapshot(snapshot_before, params={})

    assert twin.state == state_before
    assert twin.get_snapshot() == snapshot_before
    assert all(evt.type == "ControlActionProposed" for evt in engine.as_domain_events())
    assert result.actions == engine.get_latest_actions()
