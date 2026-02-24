from __future__ import annotations

from typing import Union

from .state import TwinState
from .transition import TransitionCandidate


class StateValidationError(ValueError):
    """Raised when a candidate state violates domain invariants."""



def validate_state(candidate: Union[TwinState, TransitionCandidate]) -> None:
    """Validation operator V for deterministic network + compute state."""

    if isinstance(candidate, TransitionCandidate):
        state = candidate.state
        modified_links = candidate.modified_link_indices
        modified_flows = candidate.modified_flow_ids
        modified_servers = candidate.modified_server_indices
        modified_workloads = candidate.modified_workload_ids
    else:
        state = candidate
        modified_links = tuple(range(len(state.link_backlog)))
        modified_flows = tuple(state.active_flows.keys())
        modified_servers = tuple(range(len(state.cpu_usage)))
        modified_workloads = tuple(state.active_workloads.keys())

    if state.version_counter < 0:
        raise StateValidationError("version_counter must be >= 0")
    if state.event_counter < 0:
        raise StateValidationError("event_counter must be >= 0")

    for link_id in modified_links:
        backlog = state.link_backlog[link_id]
        capacity = state.topology.link_capacity[link_id]
        if backlog < 0:
            raise StateValidationError(f"link backlog must be >= 0 (link={link_id})")
        if backlog > capacity:
            raise StateValidationError(
                f"link backlog must be <= capacity (link={link_id}, backlog={backlog}, capacity={capacity})"
            )

    for flow_id in modified_flows:
        flow = state.active_flows.get(flow_id)
        if flow is None:
            continue
        if flow.rate < 0:
            raise StateValidationError(f"flow rate must be >= 0 (flow={flow_id})")
        if flow.remaining_size < 0:
            raise StateValidationError(f"flow remaining_size must be >= 0 (flow={flow_id})")

    for server_idx in modified_servers:
        cpu = state.cpu_usage[server_idx]
        memory = state.memory_usage[server_idx]
        cpu_capacity = state.compute_topology.cpu_capacity[server_idx]
        memory_capacity = state.compute_topology.memory_capacity[server_idx]

        if cpu < 0:
            raise StateValidationError(f"cpu_usage must be >= 0 (server={server_idx})")
        if memory < 0:
            raise StateValidationError(f"memory_usage must be >= 0 (server={server_idx})")
        if cpu > cpu_capacity:
            raise StateValidationError(
                f"cpu_usage must be <= cpu_capacity (server={server_idx}, usage={cpu}, capacity={cpu_capacity})"
            )
        if state.server_workload_count[server_idx] < 0:
            raise StateValidationError(f"server_workload_count must be >= 0 (server={server_idx})")
        if memory > memory_capacity:
            raise StateValidationError(
                "memory_usage must be <= memory_capacity "
                f"(server={server_idx}, usage={memory}, capacity={memory_capacity})"
            )

    for workload_id in modified_workloads:
        workload = state.active_workloads.get(workload_id)
        if workload is None:
            continue
        if workload.cpu_demand < 0:
            raise StateValidationError(f"workload cpu_demand must be >= 0 (workload={workload_id})")
        if workload.memory_demand < 0:
            raise StateValidationError(f"workload memory_demand must be >= 0 (workload={workload_id})")
        if workload.remaining_size < 0:
            raise StateValidationError(f"workload remaining_size must be >= 0 (workload={workload_id})")
        if workload.cpu_usage_rate < 0:
            raise StateValidationError(f"workload cpu_usage_rate must be >= 0 (workload={workload_id})")
