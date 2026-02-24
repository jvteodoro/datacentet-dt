from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def test_tick_replay_produces_identical_state() -> None:
    events = [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "N1"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "N2"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "N1", "dst": "N2", "capacity": 10.0}),
        DomainEvent(timestamp=4, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 10.0, "memory_capacity": 10.0}),
        DomainEvent(
            timestamp=5,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "N1", "dst": "N2", "path": ["N1", "N2"], "rate": 5.0, "size": 3.0},
        ),
        DomainEvent(
            timestamp=6,
            type="WorkloadStarted",
            payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 2.0, "memory_demand": 1.0, "size": 2.0, "cpu_usage_rate": 1.0},
        ),
        DomainEvent(timestamp=7, type="Tick", payload={"delta_time": 1.0}),
        DomainEvent(timestamp=8, type="Tick", payload={"delta_time": 1.0}),
    ]

    a = DataCenterTwin()
    for e in events:
        a.ingest_event(e)

    b = DataCenterTwin()
    b.replay(events)

    assert b.state == a.state
    assert b.get_snapshot() == a.get_snapshot()
    assert b.event_log == a.event_log
