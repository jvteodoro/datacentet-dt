from __future__ import annotations

import os
from dataclasses import dataclass

from .seeded_generator import GeneratorProfile, InfraSize

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
class RuntimeConfig:
    profile: str
    seed: int
    source: str
    require_ingest_id: bool
    duplicate_rate: float
    infra_size: InfraSize


def parse_profile(raw: str | None) -> str:
    normalized = (raw or PROFILE_STEADY_POISSON_USERS).strip().lower()
    return normalized if normalized in SUPPORTED_PROFILES else PROFILE_STEADY_POISSON_USERS


def runtime_config_from_env() -> RuntimeConfig:
    return RuntimeConfig(
        profile=parse_profile(os.getenv("LOCUST_INGEST_PROFILE")),
        seed=int(os.getenv("LOCUST_SEED", "42")),
        source=os.getenv("LOCUST_SOURCE", "locust_ingest"),
        require_ingest_id=os.getenv("LOCUST_REQUIRE_INGEST_ID", "true").lower() != "false",
        duplicate_rate=float(os.getenv("LOCUST_DUPLICATE_RATE", "0.0")),
        infra_size=InfraSize(
            num_nodes=max(1, int(os.getenv("LOCUST_NUM_NODES", "200"))),
            num_links=max(1, int(os.getenv("LOCUST_NUM_LINKS", "400"))),
            num_servers=max(1, int(os.getenv("LOCUST_NUM_SERVERS", "100"))),
        ),
    )


def build_profile_spec(profile: str) -> GeneratorProfile:
    if profile == PROFILE_BURST_PARETO_USERS:
        return GeneratorProfile(profile, 4, 6, 2, 3, 10.0, 1.4, -0.2, 0.6, 1.1)
    if profile == PROFILE_MULTI_STREAM_SCALE:
        return GeneratorProfile(profile, 128, 5, 2, 5, 12.0, 1.7, -0.4, 0.4, 1.2)
    if profile == PROFILE_TICK_HEAVY_INFRA:
        return GeneratorProfile(profile, 8, 1, 1, 12, 14.0, 1.8, -0.5, 0.35, 1.05)
    if profile == PROFILE_MIXED_WITH_FLOWS:
        return GeneratorProfile(profile, 16, 5, 5, 4, 11.0, 1.6, -0.35, 0.45, 1.15)
    return GeneratorProfile(PROFILE_STEADY_POISSON_USERS, 8, 8, 1, 4, 9.0, 1.9, -0.45, 0.3, 1.0)
