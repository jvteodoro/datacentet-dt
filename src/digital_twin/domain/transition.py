from .event import DomainEvent
from .state import TwinState


def apply_transition(state: TwinState, event: DomainEvent) -> TwinState:
    """Transition operator H(X, e), implemented as a pure function."""

    _ = event
    return TwinState(
        version_counter=state.version_counter + 1,
        event_counter=state.event_counter + 1,
    )
