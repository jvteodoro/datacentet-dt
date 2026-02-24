from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FlowRecord:
    src_idx: int
    dst_idx: int
    path: tuple[int, ...]
    rate: float
    remaining_size: float


@dataclass(frozen=True, slots=True)
class NetworkTopology:
    node_index: dict[str, int] = field(default_factory=dict)
    reverse_node_index: tuple[str, ...] = ()
    adjacency: tuple[tuple[int, ...], ...] = ()
    link_capacity: tuple[float, ...] = ()
    link_index: dict[tuple[int, int], int] = field(default_factory=dict)


@dataclass(slots=True)
class TwinState:
    """Deterministic state X with logical immutability boundaries."""

    version_counter: int = 0
    event_counter: int = 0
    topology: NetworkTopology = field(default_factory=NetworkTopology)
    link_backlog: list[float] = field(default_factory=list)
    active_flows: dict[str, FlowRecord] = field(default_factory=dict)
