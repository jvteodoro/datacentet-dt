from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def test_per_event_updates_only_path_links() -> None:
    twin = DataCenterTwin()

    for i in range(50):
        twin.ingest_event(DomainEvent(timestamp=i + 1, type="AddNode", payload={"node_id": f"N{i}"}))

    timestamp = 100
    for i in range(49):
        twin.ingest_event(
            DomainEvent(
                timestamp=timestamp + i,
                type="AddLink",
                payload={"src": f"N{i}", "dst": f"N{i + 1}", "capacity": 10.0},
            )
        )

    before = twin.state.link_backlog
    twin.ingest_event(
        DomainEvent(
            timestamp=1000,
            type="FlowStarted",
            payload={
                "flow_id": "short",
                "src": "N10",
                "dst": "N12",
                "path": ["N10", "N11", "N12"],
                "rate": 1.0,
                "size": 5.0,
            },
        )
    )

    after = twin.state.link_backlog
    modified = {link_id for link_id, (old, new) in enumerate(zip(before, after)) if new != old}
    assert len(modified) == 2

    for link_id, (old, new) in enumerate(zip(before, after)):
        if link_id in modified:
            assert new == old + 1.0
        else:
            assert new == old
