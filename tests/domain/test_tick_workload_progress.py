from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def test_tick_completes_workload_and_updates_active_servers() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(
        DomainEvent(timestamp=1, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 20.0, "memory_capacity": 40.0})
    )
    twin.ingest_event(
        DomainEvent(
            timestamp=2,
            type="WorkloadStarted",
            payload={
                "workload_id": "W1",
                "server_id": "S1",
                "cpu_demand": 5.0,
                "memory_demand": 8.0,
                "size": 4.0,
                "cpu_usage_rate": 2.0,
            },
        )
    )

    assert "W1" in twin.state.active_workloads
    assert twin.state.active_server_indices == {0}

    twin.ingest_event(DomainEvent(timestamp=3, type="Tick", payload={"delta_time": 1.5}))
    assert twin.state.active_workloads["W1"].remaining_size == 1.0
    assert twin.state.active_server_indices == {0}

    twin.ingest_event(DomainEvent(timestamp=4, type="Tick", payload={"delta_time": 0.5}))
    assert "W1" not in twin.state.active_workloads
    assert twin.state.cpu_usage[0] == 0.0
    assert twin.state.memory_usage[0] == 0.0
    assert twin.state.active_server_indices == set()

    snapshot = twin.get_snapshot()
    assert snapshot.total_active_servers == 0
    assert snapshot.total_active_workloads == 0
