from dataclasses import dataclass

from .state import TwinState


@dataclass(frozen=True, slots=True)
class TwinSnapshot:
    """Immutable, validated-state-derived snapshot."""

    version_counter: int
    event_counter: int
    total_nodes: int
    total_links: int
    total_servers: int
    active_flows_count: int
    total_active_workloads: int
    aggregate_cpu_usage: float
    aggregate_memory_usage: float
    link_backlog: tuple[float, ...]
    cpu_usage: tuple[float, ...]
    memory_usage: tuple[float, ...]



def build_snapshot(state: TwinState) -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=state.version_counter,
        event_counter=state.event_counter,
        total_nodes=len(state.topology.reverse_node_index),
        total_links=len(state.topology.link_capacity),
        total_servers=len(state.compute_topology.reverse_server_index),
        active_flows_count=len(state.active_flows),
        total_active_workloads=len(state.active_workloads),
        aggregate_cpu_usage=sum(state.cpu_usage),
        aggregate_memory_usage=sum(state.memory_usage),
        link_backlog=tuple(state.link_backlog),
        cpu_usage=tuple(state.cpu_usage),
        memory_usage=tuple(state.memory_usage),
    )
