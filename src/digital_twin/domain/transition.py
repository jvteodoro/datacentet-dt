from __future__ import annotations

from .event import DomainEvent
from .state import FlowRecord, TwinState


def apply_transition(state: TwinState, event: DomainEvent) -> TwinState:
    """Transition operator H(X, e), implemented as a pure function."""

    event_type = event.type
    payload = event.payload

    node_index = dict(state.node_index)
    reverse_node_index = list(state.reverse_node_index)
    adjacency = [tuple(neighbors) for neighbors in state.adjacency]
    link_capacity = list(state.link_capacity)
    link_backlog = list(state.link_backlog)
    link_index = dict(state.link_index)
    active_flows = dict(state.active_flows)
    modified_links: list[int] = []
    modified_flows: list[str] = []

    if event_type == "AddNode":
        node_id = str(payload["node_id"])
        if node_id in node_index:
            raise ValueError(f"node already exists: {node_id}")
        idx = len(reverse_node_index)
        node_index[node_id] = idx
        reverse_node_index.append(node_id)
        adjacency.append(())

    elif event_type == "AddLink":
        src_idx = _node_idx(node_index, str(payload["src"]))
        dst_idx = _node_idx(node_index, str(payload["dst"]))
        capacity = float(payload["capacity"])
        edge = (src_idx, dst_idx)
        if edge in link_index:
            raise ValueError(f"link already exists: {edge}")
        link_id = len(link_capacity)
        link_index[edge] = link_id
        link_capacity.append(capacity)
        link_backlog.append(0.0)
        adjacency[src_idx] = adjacency[src_idx] + (dst_idx,)
        modified_links.append(link_id)

    elif event_type == "FlowStarted":
        flow_id = str(payload["flow_id"])
        if flow_id in active_flows:
            raise ValueError(f"flow already exists: {flow_id}")

        src_idx = _node_idx(node_index, str(payload["src"]))
        dst_idx = _node_idx(node_index, str(payload["dst"]))
        rate = float(payload["rate"])
        size = float(payload["size"])

        path_node_ids = tuple(str(node_id) for node_id in payload["path"])
        if len(path_node_ids) < 2:
            raise ValueError("path must have at least two nodes")
        path = tuple(_node_idx(node_index, node_id) for node_id in path_node_ids)

        if path[0] != src_idx or path[-1] != dst_idx:
            raise ValueError("path endpoints do not match src/dst")

        for i in range(len(path) - 1):
            link_id = _link_idx(link_index, path[i], path[i + 1])
            link_backlog[link_id] += rate
            modified_links.append(link_id)

        active_flows[flow_id] = FlowRecord(
            src_idx=src_idx,
            dst_idx=dst_idx,
            path=path,
            rate=rate,
            remaining_size=size,
        )
        modified_flows.append(flow_id)

    elif event_type == "FlowEnded":
        flow_id = str(payload["flow_id"])
        flow = active_flows.get(flow_id)
        if flow is None:
            raise ValueError(f"unknown flow: {flow_id}")
        del active_flows[flow_id]

        for i in range(len(flow.path) - 1):
            link_id = _link_idx(link_index, flow.path[i], flow.path[i + 1])
            link_backlog[link_id] -= flow.rate
            modified_links.append(link_id)
        modified_flows.append(flow_id)

    return TwinState(
        version_counter=state.version_counter + 1,
        event_counter=state.event_counter + 1,
        node_index=node_index,
        reverse_node_index=tuple(reverse_node_index),
        adjacency=tuple(adjacency),
        link_capacity=tuple(link_capacity),
        link_backlog=tuple(link_backlog),
        link_index=link_index,
        active_flows=active_flows,
        modified_link_indices=tuple(modified_links),
        modified_flow_ids=tuple(modified_flows),
    )


def _node_idx(node_index: dict[str, int], node_id: str) -> int:
    if node_id not in node_index:
        raise ValueError(f"unknown node: {node_id}")
    return node_index[node_id]


def _link_idx(link_index: dict[tuple[int, int], int], src_idx: int, dst_idx: int) -> int:
    edge = (src_idx, dst_idx)
    if edge not in link_index:
        raise ValueError(f"unknown link: {edge}")
    return link_index[edge]
