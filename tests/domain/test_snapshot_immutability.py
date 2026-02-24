from dataclasses import FrozenInstanceError

import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def test_snapshot_is_immutable_and_stable() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="tick", payload={}))

    snapshot_before = twin.get_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot_before.version_counter = 99

    twin.ingest_event(DomainEvent(timestamp=2, type="tick", payload={}))
    snapshot_after = twin.get_snapshot()

    assert snapshot_before.version_counter == 1
    assert snapshot_before.event_counter == 1
    assert snapshot_after.version_counter == 2
    assert snapshot_after.event_counter == 2
