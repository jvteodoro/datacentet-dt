import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.domain.validation import StateValidationError


def test_capacity_violation_fails_and_does_not_commit() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}))
    twin.ingest_event(DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}))
    twin.ingest_event(DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 1.0}))

    baseline_state = twin.state
    baseline_snapshot = twin.get_snapshot()
    baseline_log = twin.event_log

    with pytest.raises(StateValidationError):
        twin.ingest_event(
            DomainEvent(
                timestamp=4,
                type="FlowStarted",
                payload={
                    "flow_id": "too-fast",
                    "src": "A",
                    "dst": "B",
                    "path": ["A", "B"],
                    "rate": 2.0,
                    "size": 10.0,
                },
            )
        )

    assert twin.state == baseline_state
    assert twin.get_snapshot() == baseline_snapshot
    assert twin.event_log == baseline_log
