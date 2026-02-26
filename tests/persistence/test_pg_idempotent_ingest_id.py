from __future__ import annotations

import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.infrastructure.db.event_store_pg import AppendResult, EventStorePG


@pytest.mark.postgres
def test_pg_idempotent_ingest_id_returns_already_exists(postgres_dsn: str, ensure_postgres: None) -> None:
    store = EventStorePG(dsn=postgres_dsn, stream_id="idempotent-stream")

    event = DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"})

    assert store.append(event, version_counter=1, ingest_id=event.event_id) is AppendResult.APPENDED
    assert store.append(event, version_counter=1, ingest_id=event.event_id) is AppendResult.ALREADY_EXISTS
