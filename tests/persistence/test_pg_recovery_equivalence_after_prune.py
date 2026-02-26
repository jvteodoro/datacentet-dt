from __future__ import annotations

import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.db.event_store_pg import EventStorePG
from digital_twin.infrastructure.db.snapshot_store_pg import SnapshotStorePG


@pytest.mark.postgres
def test_pg_recovery_equivalence_after_prune(postgres_dsn: str, ensure_postgres: None) -> None:
    stream_id = "recovery-after-prune"
    event_store = EventStorePG(dsn=postgres_dsn, stream_id=stream_id)
    snapshot_store = SnapshotStorePG(dsn=postgres_dsn, stream_id=stream_id)

    uninterrupted = DataCenterTwin()
    writer = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=1)

    events = [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 8.0}),
        DomainEvent(timestamp=4, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=5, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=6, type="Tick", payload={"delta_time": 1.0}),
    ]

    for event in events:
        uninterrupted.ingest_event(event)
        writer.ingest_event(event)

    snapshot_store.prune_older_than(stream_id=stream_id, keep_last_n=2)

    recovered = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=1)
    recovered.recover()

    assert recovered.state == uninterrupted.state
    assert recovered.get_snapshot() == uninterrupted.get_snapshot()
