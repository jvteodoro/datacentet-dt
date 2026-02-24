from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def _build_twin() -> DataCenterTwin:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}))
    twin.ingest_event(DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}))
    twin.ingest_event(DomainEvent(timestamp=3, type="AddNode", payload={"node_id": "C"}))
    twin.ingest_event(DomainEvent(timestamp=4, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}))
    twin.ingest_event(DomainEvent(timestamp=5, type="AddLink", payload={"src": "B", "dst": "C", "capacity": 10.0}))
    twin.ingest_event(DomainEvent(timestamp=6, type="AddLink", payload={"src": "A", "dst": "C", "capacity": 10.0}))
    return twin


def test_start_flow_increases_backlog_only_on_path() -> None:
    twin = _build_twin()
    before = twin.state.link_backlog

    twin.ingest_event(
        DomainEvent(
            timestamp=7,
            type="FlowStarted",
            payload={
                "flow_id": "f-path",
                "src": "A",
                "dst": "C",
                "path": ["A", "B", "C"],
                "rate": 3.0,
                "size": 50.0,
            },
        )
    )

    after = twin.state.link_backlog
    idx_ab = twin.state.link_index[(twin.state.node_index["A"], twin.state.node_index["B"])]
    idx_bc = twin.state.link_index[(twin.state.node_index["B"], twin.state.node_index["C"])]
    idx_ac = twin.state.link_index[(twin.state.node_index["A"], twin.state.node_index["C"])]

    assert after[idx_ab] == before[idx_ab] + 3.0
    assert after[idx_bc] == before[idx_bc] + 3.0
    assert after[idx_ac] == before[idx_ac]


def test_end_flow_restores_previous_backlog() -> None:
    twin = _build_twin()
    baseline = twin.state.link_backlog

    start_event = DomainEvent(
        timestamp=7,
        type="FlowStarted",
        payload={
            "flow_id": "f1",
            "src": "A",
            "dst": "C",
            "path": ["A", "B", "C"],
            "rate": 2.0,
            "size": 40.0,
        },
    )
    end_event = DomainEvent(timestamp=8, type="FlowEnded", payload={"flow_id": "f1"})

    twin.ingest_event(start_event)
    twin.ingest_event(end_event)

    assert twin.state.link_backlog == baseline
