import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.domain.validation import StateValidationError


def test_compute_capacity_violation_fails_and_does_not_commit() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(
        DomainEvent(
            timestamp=1,
            type="AddServer",
            payload={"server_id": "S1", "cpu_capacity": 4.0, "memory_capacity": 8.0},
        )
    )

    baseline_state = twin.state
    baseline_snapshot = twin.get_snapshot()
    baseline_log = twin.event_log

    with pytest.raises(StateValidationError):
        twin.ingest_event(
            DomainEvent(
                timestamp=2,
                type="WorkloadStarted",
                payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 5.0, "memory_demand": 1.0},
            )
        )

    assert twin.state == baseline_state
    assert twin.get_snapshot() == baseline_snapshot
    assert twin.event_log == baseline_log
