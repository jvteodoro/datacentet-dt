from __future__ import annotations

import psycopg
import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.db.event_store_pg import EventStorePG
from digital_twin.infrastructure.db.snapshot_store_pg import SnapshotStorePG


@pytest.mark.postgres
def test_pg_snapshot_pruning_keeps_latest_n(postgres_dsn: str, ensure_postgres: None) -> None:
    stream_id = "prune-stream"
    event_store = EventStorePG(dsn=postgres_dsn, stream_id=stream_id)
    snapshot_store = SnapshotStorePG(dsn=postgres_dsn, stream_id=stream_id)
    twin = DataCenterTwin(event_store=event_store, snapshot_store=snapshot_store, snapshot_interval=1)

    events = [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 10.0, "memory_capacity": 10.0}),
        DomainEvent(timestamp=4, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 4.0}),
        DomainEvent(timestamp=5, type="Tick", payload={"delta_time": 1.0}),
    ]

    for event in events:
        twin.ingest_event(event)

    deleted = snapshot_store.prune_older_than(stream_id=stream_id, keep_last_n=3)
    assert deleted == 2

    with psycopg.connect(postgres_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT version_counter FROM snapshot_store WHERE stream_id = %s ORDER BY version_counter ASC",
                (stream_id,),
            )
            versions = [row[0] for row in cur.fetchall()]

    assert versions == [3, 4, 5]
