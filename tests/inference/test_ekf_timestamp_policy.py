from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.strategies.ekf import EKFStrategy


def _events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
        DomainEvent(timestamp=4, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 12.0, "memory_capacity": 12.0}),
        DomainEvent(timestamp=5, type="FlowStarted", payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 2.0, "size": 10.0}),
        DomainEvent(timestamp=6, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=7, type="Tick", payload={"delta_time": 1.0}),
    ]


def test_ekf_timestamp_equals_snapshot_version_and_strictly_increasing() -> None:
    registry = StrategyRegistry()
    registry.register(EKFStrategy())
    engine = InferenceEngine(registry)
    twin = DataCenterTwin()

    timestamps = []
    for event in _events():
        twin.ingest_event(event)
        snapshot = twin.get_snapshot()
        vector = engine.on_snapshot(snapshot)["ekf"]
        assert vector.timestamp == snapshot.version_counter
        timestamps.append(vector.timestamp)

    assert all(left < right for left, right in zip(timestamps, timestamps[1:]))
