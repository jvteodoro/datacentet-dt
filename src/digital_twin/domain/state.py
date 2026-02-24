from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TwinState:
    """Minimal deterministic state X for Phase 1."""

    version_counter: int = 0
    event_counter: int = 0
