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


@dataclass(frozen=True, slots=True)
class ComputeTopology:
    server_index: dict[str, int] = field(default_factory=dict)
    reverse_server_index: tuple[str, ...] = ()
    cpu_capacity: tuple[float, ...] = ()
    memory_capacity: tuple[float, ...] = ()


@dataclass(frozen=True, slots=True)
class WorkloadRecord:
    server_idx: int
    cpu_demand: float
    memory_demand: float
    remaining_size: float
    cpu_usage_rate: float


@dataclass(slots=True)
class TwinState:
    """Deterministic state X with logical immutability boundaries."""

    version_counter: int = 0
    event_counter: int = 0
    topology: NetworkTopology = field(default_factory=NetworkTopology)
    compute_topology: ComputeTopology = field(default_factory=ComputeTopology)
    link_backlog: list[float] = field(default_factory=list)
    active_flows: dict[str, FlowRecord] = field(default_factory=dict)
    cpu_usage: list[float] = field(default_factory=list)
    memory_usage: list[float] = field(default_factory=list)
    server_workload_count: list[int] = field(default_factory=list)
    active_workloads: dict[str, WorkloadRecord] = field(default_factory=dict)
    active_link_indices: set[int] = field(default_factory=set)
    active_server_indices: set[int] = field(default_factory=set)
