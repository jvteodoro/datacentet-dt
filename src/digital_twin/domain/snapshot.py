from dataclasses import dataclass

from .state import TwinState


@dataclass(frozen=True, slots=True)
class TwinSnapshot:
    """Immutable, validated-state-derived snapshot."""

    version_counter: int
    event_counter: int



def build_snapshot(state: TwinState) -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=state.version_counter,
        event_counter=state.event_counter,
    )
