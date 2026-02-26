from __future__ import annotations

import os
from dataclasses import dataclass

PROFILE_STEADY_STATE_CACHE_HIT = "steady_state_cache_hit"
PROFILE_BURST_DASHBOARD_REFRESH = "burst_dashboard_refresh"
PROFILE_REFRESH_PRESSURE = "refresh_pressure"
PROFILE_MIXED_OBSERVABILITY = "mixed_observability"

SUPPORTED_PROFILES = (
    PROFILE_STEADY_STATE_CACHE_HIT,
    PROFILE_BURST_DASHBOARD_REFRESH,
    PROFILE_REFRESH_PRESSURE,
    PROFILE_MIXED_OBSERVABILITY,
)


@dataclass(frozen=True, slots=True)
class EndpointLoad:
    name: str
    path: str
    weight: int


@dataclass(frozen=True, slots=True)
class ProfileSpec:
    name: str
    endpoints: tuple[EndpointLoad, ...]
    burst_size: int
    refresh_cycle_requests: int


@dataclass(frozen=True, slots=True)
class LocustRuntimeConfig:
    profile: str
    stop_timeout: int
    refresh_test_mode: bool
    refresh_ttl_seconds: float
    headers: dict[str, str]


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        parsed = int(raw)
    except ValueError:
        return default
    return max(0, parsed)


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        parsed = float(raw)
    except ValueError:
        return default
    return max(0.0, parsed)


def parse_headers(raw_headers: str | None) -> dict[str, str]:
    if not raw_headers:
        return {}
    headers: dict[str, str] = {}
    for piece in raw_headers.split(";"):
        part = piece.strip()
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        k = key.strip()
        v = value.strip()
        if k:
            headers[k] = v
    return headers


def parse_profile(name: str | None) -> str:
    if not name:
        return PROFILE_STEADY_STATE_CACHE_HIT
    normalized = name.strip().lower()
    if normalized in SUPPORTED_PROFILES:
        return normalized
    return PROFILE_STEADY_STATE_CACHE_HIT


def runtime_config_from_env() -> LocustRuntimeConfig:
    return LocustRuntimeConfig(
        profile=parse_profile(os.getenv("LOCUST_PROFILE")),
        stop_timeout=_int_env("LOCUST_STOP_TIMEOUT", 30),
        refresh_test_mode=os.getenv("REFRESH_TEST_MODE", "0") == "1",
        refresh_ttl_seconds=_float_env("REFRESH_TTL_SECONDS", 0.25),
        headers=parse_headers(os.getenv("LOCUST_HEADERS", "")),
    )


def _weighted_endpoint(name: str, path: str, env_weight: str, default_weight: int) -> EndpointLoad:
    return EndpointLoad(name=name, path=path, weight=_int_env(env_weight, default_weight))


def _base_endpoints() -> dict[str, EndpointLoad]:
    return {
        "health": _weighted_endpoint("health", "/health", "W_HEALTH", 1),
        "metrics": _weighted_endpoint("metrics", "/metrics", "W_METRICS", 10),
        "schema": _weighted_endpoint("schema", "/metrics/schema", "W_SCHEMA", 1),
        "streams": _weighted_endpoint("streams", "/metrics/streams", "W_STREAMS", 3),
        "top": _weighted_endpoint("top", "/metrics/top?limit=5", "W_TOP", 3),
        "histograms": _weighted_endpoint("histograms", "/metrics/histograms", "W_HIST", 3),
    }


def build_profile_spec(profile_name: str) -> ProfileSpec:
    base = _base_endpoints()

    if profile_name == PROFILE_STEADY_STATE_CACHE_HIT:
        return ProfileSpec(
            name=profile_name,
            endpoints=(
                EndpointLoad("metrics", base["metrics"].path, max(base["metrics"].weight, 1)),
                EndpointLoad("health", base["health"].path, max(base["health"].weight, 1)),
                EndpointLoad("schema", base["schema"].path, max(base["schema"].weight, 1)),
            ),
            burst_size=1,
            refresh_cycle_requests=0,
        )

    if profile_name == PROFILE_BURST_DASHBOARD_REFRESH:
        return ProfileSpec(
            name=profile_name,
            endpoints=(
                EndpointLoad("metrics", base["metrics"].path, max(base["metrics"].weight * 3, 1)),
                EndpointLoad("top", base["top"].path, max(base["top"].weight, 1)),
                EndpointLoad("histograms", base["histograms"].path, max(base["histograms"].weight, 1)),
            ),
            burst_size=max(_int_env("BURST_SIZE", 8), 1),
            refresh_cycle_requests=0,
        )

    if profile_name == PROFILE_REFRESH_PRESSURE:
        return ProfileSpec(
            name=profile_name,
            endpoints=(
                EndpointLoad("metrics", base["metrics"].path, max(base["metrics"].weight, 1)),
                EndpointLoad("streams", base["streams"].path, max(base["streams"].weight, 1)),
                EndpointLoad("top", base["top"].path, max(base["top"].weight, 1)),
            ),
            burst_size=1,
            refresh_cycle_requests=max(_int_env("REFRESH_CYCLE_REQUESTS", 8), 1),
        )

    return ProfileSpec(
        name=PROFILE_MIXED_OBSERVABILITY,
        endpoints=(
            base["metrics"],
            base["health"],
            base["schema"],
            base["streams"],
            base["top"],
            base["histograms"],
        ),
        burst_size=1,
        refresh_cycle_requests=0,
    )
