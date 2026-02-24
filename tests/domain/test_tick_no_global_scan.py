from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def test_tick_mutates_only_active_entities() -> None:
    twin = DataCenterTwin()

    for i in range(10):
        twin.ingest_event(DomainEvent(timestamp=10 + i, type="AddNode", payload={"node_id": f"N{i}"}))

    ts = 100
    for i in range(9):
        twin.ingest_event(
            DomainEvent(timestamp=ts + i, type="AddLink", payload={"src": f"N{i}", "dst": f"N{i+1}", "capacity": 10.0})
        )

    for i in range(10):
        twin.ingest_event(
            DomainEvent(
                timestamp=200 + i,
                type="AddServer",
                payload={"server_id": f"S{i}", "cpu_capacity": 20.0, "memory_capacity": 20.0},
            )
        )

    twin.ingest_event(
        DomainEvent(
            timestamp=300,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "N1", "dst": "N3", "path": ["N1", "N2", "N3"], "rate": 5.0, "size": 2.0},
        )
    )
    twin.ingest_event(
        DomainEvent(
            timestamp=301,
            type="WorkloadStarted",
            payload={"workload_id": "W1", "server_id": "S4", "cpu_demand": 3.0, "memory_demand": 2.0, "size": 4.0, "cpu_usage_rate": 1.0},
        )
    )

    before_backlog = twin.state.link_backlog
    before_cpu = twin.state.cpu_usage

    twin.ingest_event(DomainEvent(timestamp=302, type="Tick", payload={"delta_time": 0.5}))

    after = twin.state
    changed_links = {i for i, (a, b) in enumerate(zip(before_backlog, after.link_backlog)) if a != b}
    changed_servers = {i for i, (a, b) in enumerate(zip(before_cpu, after.cpu_usage)) if a != b}

    assert changed_links == {1, 2}
    assert changed_servers == set()
    assert after.active_link_indices == set()
    assert after.active_server_indices == {4}
