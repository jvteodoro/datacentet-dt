from __future__ import annotations

import psycopg
import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.infrastructure.db.event_store_pg import EventStorePG


@pytest.mark.postgres
def test_pg_eventstore_append_and_load_order(postgres_dsn: str, ensure_postgres: None) -> None:
    store = EventStorePG(dsn=postgres_dsn, stream_id="stream-A")
    events = [
        DomainEvent(timestamp=10, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=11, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=12, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
    ]

    for idx, event in enumerate(events, start=1):
        store.append(event, version_counter=idx)

    loaded = tuple(store.load_all())
    assert loaded == tuple(
        DomainEvent(timestamp=idx, type=event.type, payload=dict(event.payload), version=idx)
        for idx, event in enumerate(events, start=1)
    )

    with psycopg.connect(postgres_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version_counter FROM event_log WHERE stream_id = %s ORDER BY seq ASC", ("stream-A",))
            versions = [row[0] for row in cur.fetchall()]

    assert versions == [1, 2, 3]
