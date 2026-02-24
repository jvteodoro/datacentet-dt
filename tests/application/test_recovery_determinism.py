from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.in_memory_event_store import InMemoryEventStore
from digital_twin.infrastructure.in_memory_snapshot_store import InMemorySnapshotStore


EVENTS = [
    DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
    DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
    DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
    DomainEvent(timestamp=4, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 12.0, "memory_capacity": 12.0}),
    DomainEvent(
        timestamp=5,
        type="FlowStarted",
        payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 3.0, "size": 30.0},
    ),
    DomainEvent(
        timestamp=6,
        type="WorkloadStarted",
        payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 2.0, "memory_demand": 2.0, "size": 5.0, "cpu_usage_rate": 1.0},
    ),
    DomainEvent(timestamp=7, type="Tick", payload={"delta_time": 1.0}),
    DomainEvent(timestamp=8, type="Tick", payload={"delta_time": 1.0}),
]


def test_recovery_equals_uninterrupted_execution() -> None:
    event_store = InMemoryEventStore()
    snapshot_store = InMemorySnapshotStore()

    uninterrupted = DataCenterTwin()
    recovered_run = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=3)

    for event in EVENTS:
        uninterrupted.ingest_event(event)
        recovered_run.ingest_event(event)

    post_recovery = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=3)
    post_recovery.recover()

    assert post_recovery.state == uninterrupted.state
    assert post_recovery.get_snapshot() == uninterrupted.get_snapshot()


def test_multiple_recover_cycles_are_identical() -> None:
    event_store = InMemoryEventStore()
    snapshot_store = InMemorySnapshotStore()
    writer = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=2)

    for event in EVENTS:
        writer.ingest_event(event)

    first = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=2)
    second = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=2)

    first.recover()
    second.recover()
    second.recover()

    assert first.state == second.state
    assert first.get_snapshot() == second.get_snapshot()
