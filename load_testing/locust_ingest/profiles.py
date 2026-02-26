from __future__ import annotations

import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import NAMESPACE_URL, uuid5

PROFILE_STEADY_POISSON_USERS = "steady_poisson_users"
PROFILE_BURST_PARETO_USERS = "burst_pareto_users"
PROFILE_MULTI_STREAM_SCALE = "multi_stream_scale"
PROFILE_TICK_HEAVY_INFRA = "tick_heavy_infra"
PROFILE_MIXED_WITH_FLOWS = "mixed_with_flows"

SUPPORTED_PROFILES = (
    PROFILE_STEADY_POISSON_USERS,
    PROFILE_BURST_PARETO_USERS,
    PROFILE_MULTI_STREAM_SCALE,
    PROFILE_TICK_HEAVY_INFRA,
    PROFILE_MIXED_WITH_FLOWS,
)


@dataclass(frozen=True, slots=True)
class IngestProfileSpec:
    name: str
    stream_count: int
    workload_weight: int
    flow_weight: int
    tick_weight: int
    lambda_rate: float
    pareto_alpha: float
    lognormal_mu: float
    lognormal_sigma: float
    zipf_theta: float


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    profile: str
    seed: int
    source: str
    max_server_index: int


class SeededTrafficGenerator:
    """Deterministic event generator for HTTP ingestion load tests."""

    def __init__(self, *, spec: IngestProfileSpec, seed: int, source: str, max_server_index: int) -> None:
        self.spec = spec
        self.seed = seed
        self.source = source
        self.max_server_index = max(1, max_server_index)
        self._rng = random.Random(seed)
        self._logical_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self._counter = 0

    def next_interarrival_seconds(self) -> float:
        if self.spec.name == PROFILE_BURST_PARETO_USERS:
            return self._pareto(scale=max(1.0 / max(self.spec.lambda_rate, 1e-9), 0.001), alpha=self.spec.pareto_alpha)
        return self._rng.expovariate(max(self.spec.lambda_rate, 1e-9))

    def next_message(self) -> dict[str, Any]:
        event_type = self._pick_event_type()
        self._logical_time += timedelta(seconds=self.next_interarrival_seconds())
        stream_id = f"dc{1 + (self._counter % self.spec.stream_count)}"
        payload = self._build_payload(event_type)
        ingest_id = str(uuid5(NAMESPACE_URL, f"{self.seed}:{stream_id}:{self._counter}:{event_type}"))
        self._counter += 1
        return {
            "stream_id": stream_id,
            "ingest_id": ingest_id,
            "source": self.source,
            "source_time_utc": self._logical_time.isoformat().replace("+00:00", "Z"),
            "event_type": event_type,
            "payload": payload,
        }

    def _pick_event_type(self) -> str:
        table = [
            ("WorkloadStarted", self.spec.workload_weight),
            ("Tick", self.spec.tick_weight),
            ("FlowStarted", self.spec.flow_weight),
            ("FlowEnded", max(1, self.spec.flow_weight // 2)),
            ("WorkloadEnded", max(1, self.spec.workload_weight // 2)),
        ]
        population = [name for name, weight in table for _ in range(max(weight, 0))]
        return population[self._rng.randrange(0, len(population))]

    def _build_payload(self, event_type: str) -> dict[str, Any]:
        if event_type == "Tick":
            return {"delta_time": max(0.01, min(3.0, self._rng.lognormvariate(self.spec.lognormal_mu, self.spec.lognormal_sigma)))}
        if event_type in {"WorkloadStarted", "WorkloadEnded"}:
            workload_id = f"wl-{self._counter}"
            return {
                "workload_id": workload_id,
                "server_id": f"srv-{self._zipf_server_index()}",
                "cpu_demand": round(max(0.1, self._rng.lognormvariate(0.1, 0.2)), 6),
                "memory_demand": round(max(0.1, self._rng.lognormvariate(0.2, 0.25)), 6),
                "remaining_size": round(max(0.01, self._pareto(scale=1.0, alpha=self.spec.pareto_alpha)), 6),
            } if event_type == "WorkloadStarted" else {"workload_id": workload_id}
        flow_id = f"flow-{self._counter}"
        return {
            "flow_id": flow_id,
            "src": "A",
            "dst": "B",
            "path": ["A", "B"],
            "rate": round(max(0.1, self._rng.lognormvariate(0.0, 0.25)), 6),
            "size": round(max(0.01, self._pareto(scale=0.5, alpha=self.spec.pareto_alpha)), 6),
        } if event_type == "FlowStarted" else {"flow_id": flow_id}

    def _pareto(self, *, scale: float, alpha: float) -> float:
        u = max(self._rng.random(), 1e-12)
        return scale * (1.0 / (u ** (1.0 / max(alpha, 1e-9))))

    def _zipf_server_index(self) -> int:
        weights = [1.0 / (rank**self.spec.zipf_theta) for rank in range(1, self.max_server_index + 1)]
        total = sum(weights)
        target = self._rng.random() * total
        acc = 0.0
        for idx, weight in enumerate(weights, start=1):
            acc += weight
            if acc >= target:
                return idx
        return self.max_server_index


def parse_profile(raw: str | None) -> str:
    normalized = (raw or PROFILE_STEADY_POISSON_USERS).strip().lower()
    return normalized if normalized in SUPPORTED_PROFILES else PROFILE_STEADY_POISSON_USERS


def runtime_config_from_env() -> RuntimeConfig:
    return RuntimeConfig(
        profile=parse_profile(os.getenv("LOCUST_INGEST_PROFILE")),
        seed=int(os.getenv("LOCUST_SEED", "42")),
        source=os.getenv("LOCUST_SOURCE", "locust_ingest"),
        max_server_index=max(1, int(os.getenv("LOCUST_SERVER_COUNT", "100"))),
    )


def build_profile_spec(profile: str) -> IngestProfileSpec:
    if profile == PROFILE_BURST_PARETO_USERS:
        return IngestProfileSpec(profile, 4, 6, 2, 3, 10.0, 1.4, -0.2, 0.6, 1.1)
    if profile == PROFILE_MULTI_STREAM_SCALE:
        return IngestProfileSpec(profile, 64, 5, 2, 5, 12.0, 1.7, -0.4, 0.4, 1.2)
    if profile == PROFILE_TICK_HEAVY_INFRA:
        return IngestProfileSpec(profile, 8, 1, 1, 12, 14.0, 1.8, -0.5, 0.35, 1.05)
    if profile == PROFILE_MIXED_WITH_FLOWS:
        return IngestProfileSpec(profile, 16, 5, 5, 4, 11.0, 1.6, -0.35, 0.45, 1.15)
    return IngestProfileSpec(PROFILE_STEADY_POISSON_USERS, 8, 8, 1, 4, 9.0, 1.9, -0.45, 0.3, 1.0)
