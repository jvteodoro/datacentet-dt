from .state import TwinState


class StateValidationError(ValueError):
    """Raised when a candidate state violates domain invariants."""



def validate_state(state: TwinState) -> None:
    """Validation operator V for Phase 1."""

    if state.version_counter < 0:
        raise StateValidationError("version_counter must be >= 0")
    if state.event_counter < 0:
        raise StateValidationError("event_counter must be >= 0")
