from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.inference.engine import InferenceEngine, InferenceMode
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.strategies.moving_average import MovingAverageStrategy


def _events() -> list[DomainEvent]:
    return [
        DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
        DomainEvent(timestamp=2, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 12.0, "memory_capacity": 12.0}),
        DomainEvent(
            timestamp=3,
            type="WorkloadStarted",
            payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 1.0, "memory_demand": 1.0, "size": 2.0, "cpu_usage_rate": 1.0},
        ),
        DomainEvent(timestamp=4, type="Tick", payload={"delta_time": 1.0}),
    ]


def _engine(mode: InferenceMode) -> InferenceEngine:
    registry = StrategyRegistry()
    registry.register(MovingAverageStrategy())
    return InferenceEngine(registry, mode=mode)


def test_parameter_timestamp_strictly_increases_with_snapshots() -> None:
    twin = DataCenterTwin()
    engine = _engine(InferenceMode.LIVE)

    timestamps: list[int] = []
    for event in _events():
        twin.ingest_event(event)
        parameters = engine.on_snapshot(twin.get_snapshot())
        timestamps.append(parameters["moving_average"].timestamp)

    assert all(left < right for left, right in zip(timestamps, timestamps[1:]))


def test_replay_reproduces_same_timestamp_sequence() -> None:
    events = _events()

    twin_live = DataCenterTwin()
    twin_replay = DataCenterTwin()
    live_engine = _engine(InferenceMode.LIVE)
    replay_engine = _engine(InferenceMode.REPLAY)

    live_timestamps: list[int] = []
    replay_timestamps: list[int] = []

    for event in events:
        twin_live.ingest_event(event)
        params = live_engine.on_snapshot(twin_live.get_snapshot())
        live_timestamps.append(params["moving_average"].timestamp)

    for event in events:
        twin_replay.ingest_event(event)
        params = replay_engine.on_snapshot(twin_replay.get_snapshot())
        replay_timestamps.append(params["moving_average"].timestamp)

    assert live_timestamps == replay_timestamps
