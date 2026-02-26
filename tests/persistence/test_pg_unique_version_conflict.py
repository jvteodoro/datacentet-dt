from __future__ import annotations

import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.infrastructure.db.event_store_pg import EventStorePG, VersionConflictError


@pytest.mark.postgres
def test_pg_unique_version_conflict(postgres_dsn: str, ensure_postgres: None) -> None:
    store = EventStorePG(dsn=postgres_dsn, stream_id="version-conflict")

    first = DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"})
    second = DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"})

    store.append(first, version_counter=1)

    with pytest.raises(VersionConflictError, match="stream_id=version-conflict version_counter=1"):
        store.append(second, version_counter=1)
