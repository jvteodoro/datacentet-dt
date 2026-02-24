import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.domain.validation import StateValidationError


def test_rollback_restores_usage_and_workloads_after_failed_start() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(
        DomainEvent(
            timestamp=1,
            type="AddServer",
            payload={"server_id": "S1", "cpu_capacity": 10.0, "memory_capacity": 10.0},
        )
    )
    twin.ingest_event(
        DomainEvent(
            timestamp=2,
            type="WorkloadStarted",
            payload={"workload_id": "ok", "server_id": "S1", "cpu_demand": 3.0, "memory_demand": 3.0},
        )
    )

    before_failure = twin.state

    with pytest.raises(StateValidationError):
        twin.ingest_event(
            DomainEvent(
                timestamp=3,
                type="WorkloadStarted",
                payload={"workload_id": "bad", "server_id": "S1", "cpu_demand": 20.0, "memory_demand": 1.0},
            )
        )

    after_failure = twin.state
    assert after_failure == before_failure
    assert "bad" not in after_failure.active_workloads
