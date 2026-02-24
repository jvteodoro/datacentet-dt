from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.in_memory_event_store import InMemoryEventStore
from digital_twin.infrastructure.in_memory_snapshot_store import InMemorySnapshotStore


def _event_stream() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 10.0, "memory_capacity": 16.0}),
        DomainEvent(timestamp=4, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 5.0}),
        DomainEvent(
            timestamp=5,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 2.0, "size": 20.0},
        ),
        DomainEvent(
            timestamp=6,
            type="WorkloadStarted",
            payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 2.0, "memory_demand": 4.0, "size": 10.0, "cpu_usage_rate": 1.0},
        ),
        DomainEvent(timestamp=7, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=8, type="Tick", payload={"delta_time": 2.0}),
    ]


def test_snapshot_and_recover() -> None:
    event_store = InMemoryEventStore()
    snapshot_store = InMemorySnapshotStore()
    live = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=2)

    for event in _event_stream():
        live.ingest_event(event)

    recovered = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=2)
    recovered.recover()

    assert snapshot_store.load_latest() is not None
    assert recovered.state == live.state
    assert recovered.get_snapshot() == live.get_snapshot()
