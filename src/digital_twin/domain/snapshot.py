from dataclasses import dataclass

from .state import TwinState


@dataclass(frozen=True, slots=True)
class TwinSnapshot:
    """Immutable, validated-state-derived snapshot."""

    version_counter: int
    event_counter: int
    total_nodes: int
    total_links: int
    active_flows_count: int
    link_backlog: tuple[float, ...]



def build_snapshot(state: TwinState) -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=state.version_counter,
        event_counter=state.event_counter,
        total_nodes=len(state.reverse_node_index),
        total_links=len(state.link_capacity),
        active_flows_count=len(state.active_flows),
        link_backlog=tuple(state.link_backlog),
    )
