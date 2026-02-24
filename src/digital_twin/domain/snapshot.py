from dataclasses import dataclass

from .state import ComputeTopology, FlowRecord, NetworkTopology, TwinState, WorkloadRecord


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
    total_backlog: float
    total_active_links: int
    total_active_servers: int
    aggregate_cpu_usage: float
    aggregate_memory_usage: float
    link_backlog: tuple[float, ...]
    cpu_usage: tuple[float, ...]
    memory_usage: tuple[float, ...]
    topology_node_ids: tuple[str, ...]
    topology_adjacency: tuple[tuple[int, ...], ...]
    topology_link_capacity: tuple[float, ...]
    topology_links: tuple[tuple[int, int, int], ...]
    compute_server_ids: tuple[str, ...]
    compute_cpu_capacity: tuple[float, ...]
    compute_memory_capacity: tuple[float, ...]
    active_flows: tuple[tuple[str, FlowRecord], ...]
    server_workload_count: tuple[int, ...]
    active_workloads: tuple[tuple[str, WorkloadRecord], ...]
    active_link_indices: tuple[int, ...]
    active_server_indices: tuple[int, ...]


def build_snapshot(state: TwinState) -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=state.version_counter,
        event_counter=state.event_counter,
        total_nodes=len(state.topology.reverse_node_index),
        total_links=len(state.topology.link_capacity),
        total_servers=len(state.compute_topology.reverse_server_index),
        active_flows_count=len(state.active_flows),
        total_active_workloads=len(state.active_workloads),
        total_backlog=sum(state.link_backlog),
        total_active_links=len(state.active_link_indices),
        total_active_servers=len(state.active_server_indices),
        aggregate_cpu_usage=sum(state.cpu_usage),
        aggregate_memory_usage=sum(state.memory_usage),
        link_backlog=tuple(state.link_backlog),
        cpu_usage=tuple(state.cpu_usage),
        memory_usage=tuple(state.memory_usage),
        topology_node_ids=state.topology.reverse_node_index,
        topology_adjacency=state.topology.adjacency,
        topology_link_capacity=state.topology.link_capacity,
        topology_links=tuple((src_idx, dst_idx, link_id) for (src_idx, dst_idx), link_id in sorted(state.topology.link_index.items(), key=lambda item: item[1])),
        compute_server_ids=state.compute_topology.reverse_server_index,
        compute_cpu_capacity=state.compute_topology.cpu_capacity,
        compute_memory_capacity=state.compute_topology.memory_capacity,
        active_flows=tuple(sorted(state.active_flows.items())),
        server_workload_count=tuple(state.server_workload_count),
        active_workloads=tuple(sorted(state.active_workloads.items())),
        active_link_indices=tuple(sorted(state.active_link_indices)),
        active_server_indices=tuple(sorted(state.active_server_indices)),
    )


def state_from_snapshot(snapshot: TwinSnapshot) -> TwinState:
    topology = NetworkTopology(
        node_index={node_id: idx for idx, node_id in enumerate(snapshot.topology_node_ids)},
        reverse_node_index=snapshot.topology_node_ids,
        adjacency=snapshot.topology_adjacency,
        link_capacity=snapshot.topology_link_capacity,
        link_index={(src_idx, dst_idx): link_id for src_idx, dst_idx, link_id in snapshot.topology_links},
    )
    compute_topology = ComputeTopology(
        server_index={server_id: idx for idx, server_id in enumerate(snapshot.compute_server_ids)},
        reverse_server_index=snapshot.compute_server_ids,
        cpu_capacity=snapshot.compute_cpu_capacity,
        memory_capacity=snapshot.compute_memory_capacity,
    )
    return TwinState(
        version_counter=snapshot.version_counter,
        event_counter=snapshot.event_counter,
        topology=topology,
        compute_topology=compute_topology,
        link_backlog=list(snapshot.link_backlog),
        active_flows=dict(snapshot.active_flows),
        cpu_usage=list(snapshot.cpu_usage),
        memory_usage=list(snapshot.memory_usage),
        server_workload_count=list(snapshot.server_workload_count),
        active_workloads=dict(snapshot.active_workloads),
        active_link_indices=set(snapshot.active_link_indices),
        active_server_indices=set(snapshot.active_server_indices),
    )
