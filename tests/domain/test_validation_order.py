import pytest

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.state import TwinState
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.domain.validation import StateValidationError


def test_validation_runs_before_persistence_and_commit() -> None:
    calls: list[str] = []

    def transition(state: TwinState, event: DomainEvent) -> TwinState:
        _ = event
        calls.append("transition")
        return TwinState(
            version_counter=state.version_counter + 1,
            event_counter=state.event_counter + 1,
        )

    def validator(state: TwinState) -> None:
        _ = state
        calls.append("validate")
        raise StateValidationError("forced invalid")

    twin = DataCenterTwin(transition_fn=transition, validator_fn=validator)
    baseline_state = twin.state
    baseline_snapshot = twin.get_snapshot()

    with pytest.raises(StateValidationError):
        twin.ingest_event(DomainEvent(timestamp=1, type="invalid", payload={}))

    assert calls == ["transition", "validate"]
    assert twin.state == baseline_state
    assert twin.get_snapshot() == baseline_snapshot
    assert twin.event_log == ()
    assert twin.metrics.events_processed_total == 0
