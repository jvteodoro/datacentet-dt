from uuid import UUID

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin


def _deterministic_events(n: int) -> list[DomainEvent]:
    return [
        DomainEvent(
            event_id=UUID(int=i + 1),
            timestamp=i,
            type="tick",
            payload={"index": i},
            version=1,
        )
        for i in range(n)
    ]


def test_replay_produces_identical_state_and_snapshot() -> None:
    events = _deterministic_events(25)

    ingested = DataCenterTwin()
    for event in events:
        ingested.ingest_event(event)

    replayed = DataCenterTwin()
    replayed.replay(events)

    assert replayed.state == ingested.state
    assert replayed.get_snapshot() == ingested.get_snapshot()
    assert replayed.event_log == ingested.event_log
