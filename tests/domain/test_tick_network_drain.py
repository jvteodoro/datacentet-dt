from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def test_tick_drains_backlog_and_updates_active_links() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "N1"}))
    twin.ingest_event(DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "N2"}))
    twin.ingest_event(
        DomainEvent(timestamp=3, type="AddLink", payload={"src": "N1", "dst": "N2", "capacity": 10.0})
    )
    twin.ingest_event(
        DomainEvent(
            timestamp=4,
            type="FlowStarted",
            payload={"flow_id": "F1", "src": "N1", "dst": "N2", "path": ["N1", "N2"], "rate": 6.0, "size": 3.0},
        )
    )

    assert twin.state.active_link_indices == {0}
    assert twin.state.link_backlog[0] == 6.0

    twin.ingest_event(DomainEvent(timestamp=5, type="Tick", payload={"delta_time": 0.2}))
    assert twin.state.link_backlog[0] == 4.0
    assert twin.state.active_link_indices == {0}

    twin.ingest_event(DomainEvent(timestamp=6, type="Tick", payload={"delta_time": 1.0}))
    assert twin.state.link_backlog[0] == 0.0
    assert twin.state.active_link_indices == set()

    snapshot = twin.get_snapshot()
    assert snapshot.total_backlog == 0.0
    assert snapshot.total_active_links == 0
