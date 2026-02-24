from __future__ import annotations

from typing import Union

from .state import TwinState
from .transition import TransitionCandidate


class StateValidationError(ValueError):
    """Raised when a candidate state violates domain invariants."""



def validate_state(candidate: Union[TwinState, TransitionCandidate]) -> None:
    """Validation operator V for deterministic flow-level network state."""

    if isinstance(candidate, TransitionCandidate):
        state = candidate.state
        modified_links = candidate.modified_link_indices
        modified_flows = candidate.modified_flow_ids
    else:
        state = candidate
        modified_links = tuple(range(len(state.link_backlog)))
        modified_flows = tuple(state.active_flows.keys())

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
