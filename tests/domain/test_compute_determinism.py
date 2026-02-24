from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def _compute_events() -> list[DomainEvent]:
    return [
        DomainEvent(
            timestamp=1,
            type="AddServer",
            payload={"server_id": "S1", "cpu_capacity": 16.0, "memory_capacity": 64.0},
        ),
        DomainEvent(
            timestamp=2,
            type="WorkloadStarted",
            payload={
                "workload_id": "W1",
                "server_id": "S1",
                "cpu_demand": 4.0,
                "memory_demand": 10.0,
            },
        ),
        DomainEvent(timestamp=3, type="WorkloadEnded", payload={"workload_id": "W1"}),
        DomainEvent(
            timestamp=4,
            type="WorkloadStarted",
            payload={
                "workload_id": "W2",
                "server_id": "S1",
                "cpu_demand": 6.0,
                "memory_demand": 12.0,
            },
        ),
    ]


def test_compute_replay_produces_identical_state_and_snapshot() -> None:
    events = _compute_events()

    ingested = DataCenterTwin()
    for event in events:
        ingested.ingest_event(event)

    replayed = DataCenterTwin()
    replayed.replay(events)

    assert replayed.state == ingested.state
    assert replayed.get_snapshot() == ingested.get_snapshot()
    assert replayed.event_log == ingested.event_log


def test_workload_started_and_ended_update_local_usage() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(
        DomainEvent(
            timestamp=1,
            type="AddServer",
            payload={"server_id": "S1", "cpu_capacity": 8.0, "memory_capacity": 32.0},
        )
    )

    twin.ingest_event(
        DomainEvent(
            timestamp=2,
            type="WorkloadStarted",
            payload={"workload_id": "A", "server_id": "S1", "cpu_demand": 2.0, "memory_demand": 5.0},
        )
    )

    after_start = twin.state
    assert after_start.cpu_usage == [2.0]
    assert after_start.memory_usage == [5.0]
    assert "A" in after_start.active_workloads

    twin.ingest_event(DomainEvent(timestamp=3, type="WorkloadEnded", payload={"workload_id": "A"}))

    after_end = twin.state
    assert after_end.cpu_usage == [0.0]
    assert after_end.memory_usage == [0.0]
    assert "A" not in after_end.active_workloads
