from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def _topology_events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddNode", payload={"node_id": "C"}),
        DomainEvent(timestamp=4, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
        DomainEvent(timestamp=5, type="AddLink", payload={"src": "B", "dst": "C", "capacity": 20.0}),
        DomainEvent(
            timestamp=6,
            type="FlowStarted",
            payload={
                "flow_id": "f1",
                "src": "A",
                "dst": "C",
                "path": ["A", "B", "C"],
                "rate": 2.5,
                "size": 100.0,
            },
        ),
    ]


def test_add_nodes_and_links_replay_equality() -> None:
    events = _topology_events()

    a = DataCenterTwin()
    for event in events:
        a.ingest_event(event)

    b = DataCenterTwin()
    b.replay(events)

    assert a.state.node_index == b.state.node_index
    assert a.state.reverse_node_index == b.state.reverse_node_index
    assert a.state.link_capacity == b.state.link_capacity
    assert a.state.link_backlog == b.state.link_backlog
    assert a.state.active_flows == b.state.active_flows
    assert a.get_snapshot() == b.get_snapshot()
