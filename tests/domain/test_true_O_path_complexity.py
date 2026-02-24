import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.domain.validation import StateValidationError


def _build_twin() -> DataCenterTwin:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}))
    twin.ingest_event(DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}))
    twin.ingest_event(DomainEvent(timestamp=3, type="AddNode", payload={"node_id": "C"}))
    twin.ingest_event(DomainEvent(timestamp=4, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 5.0}))
    twin.ingest_event(DomainEvent(timestamp=5, type="AddLink", payload={"src": "B", "dst": "C", "capacity": 5.0}))
    return twin


def test_flow_started_keeps_same_internal_backlog_list_object() -> None:
    twin = _build_twin()
    backlog_id = id(twin._state.link_backlog)

    twin.ingest_event(
        DomainEvent(
            timestamp=6,
            type="FlowStarted",
            payload={
                "flow_id": "f1",
                "src": "A",
                "dst": "C",
                "path": ["A", "B", "C"],
                "rate": 1.0,
                "size": 9.0,
            },
        )
    )

    assert id(twin._state.link_backlog) == backlog_id


def test_flow_ended_keeps_same_internal_active_flows_dict_object() -> None:
    twin = _build_twin()
    twin.ingest_event(
        DomainEvent(
            timestamp=6,
            type="FlowStarted",
            payload={
                "flow_id": "f1",
                "src": "A",
                "dst": "C",
                "path": ["A", "B", "C"],
                "rate": 1.0,
                "size": 9.0,
            },
        )
    )
    flows_id = id(twin._state.active_flows)

    twin.ingest_event(DomainEvent(timestamp=7, type="FlowEnded", payload={"flow_id": "f1"}))

    assert id(twin._state.active_flows) == flows_id


def test_validation_failure_rolls_back_backlog_and_flow_in_place() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}))
    twin.ingest_event(DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}))
    twin.ingest_event(DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 1.0}))

    backlog_before = tuple(twin._state.link_backlog)
    flow_ids_before = tuple(twin._state.active_flows.keys())
    version_before = twin._state.version_counter
    event_before = twin._state.event_counter

    with pytest.raises(StateValidationError):
        twin.ingest_event(
            DomainEvent(
                timestamp=4,
                type="FlowStarted",
                payload={
                    "flow_id": "overflow",
                    "src": "A",
                    "dst": "B",
                    "path": ["A", "B"],
                    "rate": 3.0,
                    "size": 3.0,
                },
            )
        )

    assert tuple(twin._state.link_backlog) == backlog_before
    assert tuple(twin._state.active_flows.keys()) == flow_ids_before
    assert twin._state.version_counter == version_before
    assert twin._state.event_counter == event_before


def test_replay_and_snapshot_immutability_preserved() -> None:
    events = [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 3.0}),
        DomainEvent(
            timestamp=4,
            type="FlowStarted",
            payload={"flow_id": "f1", "src": "A", "dst": "B", "path": ["A", "B"], "rate": 1.0, "size": 4.0},
        ),
    ]

    a = DataCenterTwin()
    for event in events:
        a.ingest_event(event)

    b = DataCenterTwin()
    b.replay(events)

    assert a.state == b.state
    snap = a.get_snapshot()
    assert isinstance(snap.link_backlog, tuple)
