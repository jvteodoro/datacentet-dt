from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def _build_twin() -> DataCenterTwin:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}))
    twin.ingest_event(DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}))
    twin.ingest_event(DomainEvent(timestamp=3, type="AddNode", payload={"node_id": "C"}))
    twin.ingest_event(DomainEvent(timestamp=4, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}))
    twin.ingest_event(DomainEvent(timestamp=5, type="AddLink", payload={"src": "B", "dst": "C", "capacity": 10.0}))
    return twin


def test_flow_started_keeps_topology_identity_and_changes_dynamic_refs_only() -> None:
    twin = _build_twin()
    top0 = twin.state.topology
    node_index_id = id(top0.node_index)
    adjacency_id = id(top0.adjacency)
    backlog_id = id(twin.state.link_backlog)
    flows_id = id(twin.state.active_flows)

    twin.ingest_event(
        DomainEvent(
            timestamp=10,
            type="FlowStarted",
            payload={
                "flow_id": "f1",
                "src": "A",
                "dst": "C",
                "path": ["A", "B", "C"],
                "rate": 1.0,
                "size": 10.0,
            },
        )
    )

    assert twin.state.topology is top0
    assert id(twin.state.topology.node_index) == node_index_id
    assert id(twin.state.topology.adjacency) == adjacency_id
    assert id(twin.state.link_backlog) != backlog_id
    assert id(twin.state.active_flows) != flows_id


def test_flow_ended_keeps_topology_identity_and_changes_dynamic_refs_only() -> None:
    twin = _build_twin()
    twin.ingest_event(
        DomainEvent(
            timestamp=10,
            type="FlowStarted",
            payload={
                "flow_id": "f1",
                "src": "A",
                "dst": "C",
                "path": ["A", "B", "C"],
                "rate": 1.0,
                "size": 10.0,
            },
        )
    )

    top1 = twin.state.topology
    node_index_id = id(top1.node_index)
    adjacency_id = id(top1.adjacency)
    backlog_id = id(twin.state.link_backlog)
    flows_id = id(twin.state.active_flows)

    twin.ingest_event(DomainEvent(timestamp=11, type="FlowEnded", payload={"flow_id": "f1"}))

    assert twin.state.topology is top1
    assert id(twin.state.topology.node_index) == node_index_id
    assert id(twin.state.topology.adjacency) == adjacency_id
    assert id(twin.state.link_backlog) != backlog_id
    assert id(twin.state.active_flows) != flows_id


def test_modified_indices_not_in_committed_state_and_replay_equal() -> None:
    events = [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
        DomainEvent(
            timestamp=4,
            type="FlowStarted",
            payload={"flow_id": "f1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 2.0, "size": 8.0},
        ),
    ]

    ingested = DataCenterTwin()
    for event in events:
        ingested.ingest_event(event)

    assert not hasattr(ingested.state, "modified_link_indices")
    assert not hasattr(ingested.state, "modified_flow_ids")

    replayed = DataCenterTwin()
    replayed.replay(events)

    assert replayed.state == ingested.state
