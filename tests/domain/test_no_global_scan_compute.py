from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def test_workload_event_updates_only_target_server_usage() -> None:
    twin = DataCenterTwin()

    for i in range(120):
        twin.ingest_event(
            DomainEvent(
                timestamp=i + 1,
                type="AddServer",
                payload={"server_id": f"S{i}", "cpu_capacity": 50.0, "memory_capacity": 100.0},
            )
        )

    before_cpu = twin.state.cpu_usage
    before_memory = twin.state.memory_usage

    twin.ingest_event(
        DomainEvent(
            timestamp=1000,
            type="WorkloadStarted",
            payload={"workload_id": "W-target", "server_id": "S77", "cpu_demand": 7.0, "memory_demand": 11.0},
        )
    )

    after = twin.state

    changed_cpu = {idx for idx, (old, new) in enumerate(zip(before_cpu, after.cpu_usage)) if old != new}
    changed_memory = {idx for idx, (old, new) in enumerate(zip(before_memory, after.memory_usage)) if old != new}

    assert changed_cpu == {77}
    assert changed_memory == {77}
    assert after.cpu_usage[77] == before_cpu[77] + 7.0
    assert after.memory_usage[77] == before_memory[77] + 11.0
