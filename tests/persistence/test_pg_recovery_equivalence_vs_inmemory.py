from __future__ import annotations

import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.db.event_store_pg import EventStorePG
from digital_twin.infrastructure.db.snapshot_store_pg import SnapshotStorePG
from digital_twin.infrastructure.in_memory_event_store import InMemoryEventStore
from digital_twin.infrastructure.in_memory_snapshot_store import InMemorySnapshotStore


EVENTS = [
    DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
    DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
    DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
    DomainEvent(timestamp=4, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 12.0, "memory_capacity": 12.0}),
    DomainEvent(timestamp=5, type="FlowStarted", payload={"flow_id": "F1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 3.0, "size": 30.0}),
    DomainEvent(timestamp=6, type="WorkloadStarted", payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 2.0, "memory_demand": 2.0, "size": 5.0, "cpu_usage_rate": 1.0}),
    DomainEvent(timestamp=7, type="Tick", payload={"delta_time": 1.0}),
    DomainEvent(timestamp=8, type="Tick", payload={"delta_time": 1.0}),
]


@pytest.mark.postgres
def test_pg_and_inmemory_equivalence_for_same_event_stream(postgres_dsn: str, ensure_postgres: None) -> None:
    mem = DataCenterTwin(event_store=InMemoryEventStore(), snapshot_store=InMemorySnapshotStore(), snapshot_interval=3)

    pg = DataCenterTwin(
        event_store=EventStorePG(dsn=postgres_dsn, stream_id="equivalence"),
        snapshot_store=SnapshotStorePG(dsn=postgres_dsn, stream_id="equivalence"),
        snapshot_interval=3,
    )

    for event in EVENTS:
        mem.ingest_event(event)
        pg.ingest_event(event)

    pg_recovered = DataCenterTwin(
        event_store=EventStorePG(dsn=postgres_dsn, stream_id="equivalence"),
        snapshot_store=SnapshotStorePG(dsn=postgres_dsn, stream_id="equivalence"),
        snapshot_interval=3,
    )
    pg_recovered.recover()

    assert pg_recovered.state == mem.state
    assert pg_recovered.get_snapshot() == mem.get_snapshot()
