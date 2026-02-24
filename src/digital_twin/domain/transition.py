from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .event import DomainEvent
from .state import ComputeTopology, FlowRecord, NetworkTopology, TwinState, WorkloadRecord


@dataclass(frozen=True, slots=True)
class TransitionCandidate:
    state: TwinState
    modified_link_indices: tuple[int, ...] = ()
    modified_flow_ids: tuple[str, ...] = ()
    modified_server_indices: tuple[int, ...] = ()
    modified_workload_ids: tuple[str, ...] = ()
    rollback_actions: tuple[Callable[[], None], ...] = field(default_factory=tuple)

    def rollback(self) -> None:
        for action in reversed(self.rollback_actions):
            action()


# Architectural alignment:
# - system_blueprint: sparse event-driven evolution with deterministic H.
# - performance_budget: strict local updates for flow/workload events.
# - determinism_and_replay: sequential deterministic evolution.
# - flow_level_contracts: local link/server constraints feed V before commit.
def apply_transition(state: TwinState, event: DomainEvent) -> TransitionCandidate:
    event_type = event.type
    payload = event.payload

    topology = state.topology
    compute_topology = state.compute_topology
    modified_links: list[int] = []
    modified_flows: list[str] = []
    modified_servers: list[int] = []
    modified_workloads: list[str] = []
    rollback_actions: list[Callable[[], None]] = []

    old_version = state.version_counter
    old_event = state.event_counter

    if event_type == "AddNode":
        node_id = str(payload["node_id"])
        if node_id in topology.node_index:
            raise ValueError(f"node already exists: {node_id}")

        node_index = dict(topology.node_index)
        reverse_node_index = list(topology.reverse_node_index)
        adjacency = list(topology.adjacency)

        idx = len(reverse_node_index)
        node_index[node_id] = idx
        reverse_node_index.append(node_id)
        adjacency.append(())

        old_topology = state.topology
        state.topology = NetworkTopology(
            node_index=node_index,
            reverse_node_index=tuple(reverse_node_index),
            adjacency=tuple(adjacency),
            link_capacity=topology.link_capacity,
            link_index=topology.link_index,
        )
        rollback_actions.append(lambda old=old_topology: setattr(state, "topology", old))

    elif event_type == "AddLink":
        src_idx = _node_idx(topology.node_index, str(payload["src"]))
        dst_idx = _node_idx(topology.node_index, str(payload["dst"]))
        capacity = float(payload["capacity"])
        edge = (src_idx, dst_idx)
        if edge in topology.link_index:
            raise ValueError(f"link already exists: {edge}")

        link_index = dict(topology.link_index)
        link_capacity = list(topology.link_capacity)
        adjacency = list(topology.adjacency)

        link_id = len(link_capacity)
        link_index[edge] = link_id
        link_capacity.append(capacity)
        adjacency[src_idx] = adjacency[src_idx] + (dst_idx,)

        old_topology = state.topology
        old_backlog_len = len(state.link_backlog)

        state.topology = NetworkTopology(
            node_index=topology.node_index,
            reverse_node_index=topology.reverse_node_index,
            adjacency=tuple(adjacency),
            link_capacity=tuple(link_capacity),
            link_index=link_index,
        )
        state.link_backlog.append(0.0)

        rollback_actions.append(lambda old=old_topology: setattr(state, "topology", old))
        rollback_actions.append(lambda length=old_backlog_len: _truncate_list(state.link_backlog, length))
        modified_links.append(link_id)

    elif event_type == "FlowStarted":
        flow_id = str(payload["flow_id"])
        if flow_id in state.active_flows:
            raise ValueError(f"flow already exists: {flow_id}")

        src_idx = _node_idx(topology.node_index, str(payload["src"]))
        dst_idx = _node_idx(topology.node_index, str(payload["dst"]))
        rate = float(payload["rate"])
        size = float(payload["size"])

        path_node_ids = tuple(str(node_id) for node_id in payload["path"])
        if len(path_node_ids) < 2:
            raise ValueError("path must have at least two nodes")
        path = tuple(_node_idx(topology.node_index, node_id) for node_id in path_node_ids)
        if path[0] != src_idx or path[-1] != dst_idx:
            raise ValueError("path endpoints do not match src/dst")

        old_values: list[tuple[int, float]] = []
        for i in range(len(path) - 1):
            link_id = _link_idx(topology.link_index, path[i], path[i + 1])
            old_values.append((link_id, state.link_backlog[link_id]))
            state.link_backlog[link_id] += rate
            modified_links.append(link_id)

        flow_record = FlowRecord(
            src_idx=src_idx,
            dst_idx=dst_idx,
            path=path,
            rate=rate,
            remaining_size=size,
        )
        state.active_flows[flow_id] = flow_record
        modified_flows.append(flow_id)

        rollback_actions.append(lambda saved=tuple(old_values): _restore_backlog(state.link_backlog, saved))
        rollback_actions.append(lambda fid=flow_id: state.active_flows.pop(fid, None))

    elif event_type == "FlowEnded":
        flow_id = str(payload["flow_id"])
        flow = state.active_flows.get(flow_id)
        if flow is None:
            raise ValueError(f"unknown flow: {flow_id}")

        old_values: list[tuple[int, float]] = []
        for i in range(len(flow.path) - 1):
            link_id = _link_idx(topology.link_index, flow.path[i], flow.path[i + 1])
            old_values.append((link_id, state.link_backlog[link_id]))
            state.link_backlog[link_id] -= flow.rate
            modified_links.append(link_id)

        del state.active_flows[flow_id]
        modified_flows.append(flow_id)

        rollback_actions.append(lambda saved=tuple(old_values): _restore_backlog(state.link_backlog, saved))
        rollback_actions.append(lambda fid=flow_id, rec=flow: state.active_flows.__setitem__(fid, rec))

    elif event_type == "AddServer":
        server_id = str(payload["server_id"])
        if server_id in compute_topology.server_index:
            raise ValueError(f"server already exists: {server_id}")

        cpu_capacity = float(payload["cpu_capacity"])
        memory_capacity = float(payload["memory_capacity"])

        server_index = dict(compute_topology.server_index)
        reverse_server_index = list(compute_topology.reverse_server_index)
        cpu_capacity_values = list(compute_topology.cpu_capacity)
        memory_capacity_values = list(compute_topology.memory_capacity)

        server_idx = len(reverse_server_index)
        server_index[server_id] = server_idx
        reverse_server_index.append(server_id)
        cpu_capacity_values.append(cpu_capacity)
        memory_capacity_values.append(memory_capacity)

        old_compute_topology = state.compute_topology
        old_cpu_usage_len = len(state.cpu_usage)
        old_memory_usage_len = len(state.memory_usage)

        state.compute_topology = ComputeTopology(
            server_index=server_index,
            reverse_server_index=tuple(reverse_server_index),
            cpu_capacity=tuple(cpu_capacity_values),
            memory_capacity=tuple(memory_capacity_values),
        )
        state.cpu_usage.append(0.0)
        state.memory_usage.append(0.0)

        rollback_actions.append(lambda old=old_compute_topology: setattr(state, "compute_topology", old))
        rollback_actions.append(lambda length=old_cpu_usage_len: _truncate_list(state.cpu_usage, length))
        rollback_actions.append(lambda length=old_memory_usage_len: _truncate_list(state.memory_usage, length))
        modified_servers.append(server_idx)

    elif event_type == "WorkloadStarted":
        workload_id = str(payload["workload_id"])
        if workload_id in state.active_workloads:
            raise ValueError(f"workload already exists: {workload_id}")

        server_idx = _server_idx(compute_topology.server_index, str(payload["server_id"]))
        cpu_demand = float(payload["cpu_demand"])
        memory_demand = float(payload["memory_demand"])

        old_cpu = state.cpu_usage[server_idx]
        old_memory = state.memory_usage[server_idx]

        state.cpu_usage[server_idx] += cpu_demand
        state.memory_usage[server_idx] += memory_demand
        modified_servers.append(server_idx)

        workload = WorkloadRecord(
            server_idx=server_idx,
            cpu_demand=cpu_demand,
            memory_demand=memory_demand,
        )
        state.active_workloads[workload_id] = workload
        modified_workloads.append(workload_id)

        rollback_actions.append(
            lambda idx=server_idx, cpu=old_cpu, mem=old_memory: _restore_server_usage(state, idx, cpu, mem)
        )
        rollback_actions.append(lambda wid=workload_id: state.active_workloads.pop(wid, None))

    elif event_type == "WorkloadEnded":
        workload_id = str(payload["workload_id"])
        workload = state.active_workloads.get(workload_id)
        if workload is None:
            raise ValueError(f"unknown workload: {workload_id}")

        server_idx = workload.server_idx
        old_cpu = state.cpu_usage[server_idx]
        old_memory = state.memory_usage[server_idx]

        state.cpu_usage[server_idx] -= workload.cpu_demand
        state.memory_usage[server_idx] -= workload.memory_demand
        modified_servers.append(server_idx)

        del state.active_workloads[workload_id]
        modified_workloads.append(workload_id)

        rollback_actions.append(
            lambda idx=server_idx, cpu=old_cpu, mem=old_memory: _restore_server_usage(state, idx, cpu, mem)
        )
        rollback_actions.append(lambda wid=workload_id, rec=workload: state.active_workloads.__setitem__(wid, rec))

    state.version_counter = old_version + 1
    state.event_counter = old_event + 1
    rollback_actions.append(lambda value=old_version: setattr(state, "version_counter", value))
    rollback_actions.append(lambda value=old_event: setattr(state, "event_counter", value))

    return TransitionCandidate(
        state=state,
        modified_link_indices=tuple(modified_links),
        modified_flow_ids=tuple(modified_flows),
        modified_server_indices=tuple(modified_servers),
        modified_workload_ids=tuple(modified_workloads),
        rollback_actions=tuple(rollback_actions),
    )


def _truncate_list(items: list[float], length: int) -> None:
    del items[length:]


def _restore_backlog(backlog: list[float], saved: tuple[tuple[int, float], ...]) -> None:
    for link_id, old_value in saved:
        backlog[link_id] = old_value


def _restore_server_usage(state: TwinState, server_idx: int, cpu_value: float, memory_value: float) -> None:
    state.cpu_usage[server_idx] = cpu_value
    state.memory_usage[server_idx] = memory_value


def _node_idx(node_index: dict[str, int], node_id: str) -> int:
    if node_id not in node_index:
        raise ValueError(f"unknown node: {node_id}")
    return node_index[node_id]


def _link_idx(link_index: dict[tuple[int, int], int], src_idx: int, dst_idx: int) -> int:
    edge = (src_idx, dst_idx)
    if edge not in link_index:
        raise ValueError(f"unknown link: {edge}")
    return link_index[edge]


def _server_idx(server_index: dict[str, int], server_id: str) -> int:
    if server_id not in server_index:
        raise ValueError(f"unknown server: {server_id}")
    return server_index[server_id]
