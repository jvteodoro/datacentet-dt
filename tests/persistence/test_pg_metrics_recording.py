from __future__ import annotations

import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.infrastructure.db.event_store_pg import EventStorePG


@pytest.mark.postgres
def test_pg_metrics_recording_on_forced_error() -> None:
    invalid_dsn = "postgresql://invalid:invalid@127.0.0.1:1/invalid"
    store = EventStorePG(dsn=invalid_dsn, stream_id="metrics-errors")

    with pytest.raises(Exception):
        store.append(DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}), version_counter=1)

    assert store.metrics.db_event_append_errors_total >= 1
    assert store.metrics.db_query_errors_total >= 1
