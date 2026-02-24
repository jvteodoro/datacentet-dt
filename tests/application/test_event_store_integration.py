from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.in_memory_event_store import InMemoryEventStore
from digital_twin.infrastructure.in_memory_snapshot_store import InMemorySnapshotStore


def _events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
        DomainEvent(
            timestamp=4,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 3.0, "size": 10.0},
        ),
    ]


def test_append_events_and_recover_state() -> None:
    event_store = InMemoryEventStore()
    snapshot_store = InMemorySnapshotStore()
    ingested = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store)

    for event in _events():
        ingested.ingest_event(event)

    recovered = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store)
    recovered.recover()

    assert recovered.state == ingested.state
    assert recovered.get_snapshot() == ingested.get_snapshot()


def test_event_ordering_preserved_exactly() -> None:
    event_store = InMemoryEventStore()
    twin = DataCenterTwin(event_store=event_store, snapshot_store=InMemorySnapshotStore())

    events = _events()
    for event in events:
        twin.ingest_event(event)

    assert tuple(event_store.load_all()) == tuple(twin.event_log)
    assert tuple(event_store.load_all()) == tuple(events)
