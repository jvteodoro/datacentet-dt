from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KafkaProfile:
    name: str
    stream_count: int
    target_rps: int
    duration_s: int
    hot_stream_probability: float


PROFILES = {
    "uniform_streams": KafkaProfile("uniform_streams", 128, 2000, 60, 0.0),
    "hot_stream": KafkaProfile("hot_stream", 128, 2000, 60, 0.8),
    "burst_streams": KafkaProfile("burst_streams", 256, 3000, 60, 0.2),
    "rebalance_churn": KafkaProfile("rebalance_churn", 128, 2500, 120, 0.4),
    "steady_poisson_users": KafkaProfile("steady_poisson_users", 8, 1000, 60, 0.0),
    "multi_stream_scale": KafkaProfile("multi_stream_scale", 256, 2000, 90, 0.0),
}


def load_profile(name: str) -> KafkaProfile:
    return PROFILES.get(name, PROFILES["uniform_streams"])
