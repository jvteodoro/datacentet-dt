from __future__ import annotations

from load_testing.locust import profiles


def test_parse_profile_defaults_to_steady_state() -> None:
    assert profiles.parse_profile(None) == profiles.PROFILE_STEADY_STATE_CACHE_HIT
    assert profiles.parse_profile("unknown") == profiles.PROFILE_STEADY_STATE_CACHE_HIT


def test_parse_headers_supports_semicolon_pairs() -> None:
    parsed = profiles.parse_headers("Authorization=Bearer token;X-Trace-Id=abc123")
    assert parsed == {"Authorization": "Bearer token", "X-Trace-Id": "abc123"}


def test_mixed_profile_uses_expected_default_paths(monkeypatch) -> None:
    monkeypatch.delenv("W_HEALTH", raising=False)
    monkeypatch.delenv("W_METRICS", raising=False)
    monkeypatch.delenv("W_SCHEMA", raising=False)
    monkeypatch.delenv("W_STREAMS", raising=False)
    monkeypatch.delenv("W_TOP", raising=False)
    monkeypatch.delenv("W_HIST", raising=False)

    spec = profiles.build_profile_spec(profiles.PROFILE_MIXED_OBSERVABILITY)
    endpoint_paths = {endpoint.path for endpoint in spec.endpoints}

    assert "/health" in endpoint_paths
    assert "/metrics" in endpoint_paths
    assert "/metrics/schema" in endpoint_paths
    assert "/metrics/streams" in endpoint_paths
    assert "/metrics/top?limit=5" in endpoint_paths
    assert "/metrics/histograms" in endpoint_paths


def test_weight_parsing_uses_defaults_for_invalid_env(monkeypatch) -> None:
    monkeypatch.setenv("W_METRICS", "invalid")
    spec = profiles.build_profile_spec(profiles.PROFILE_MIXED_OBSERVABILITY)
    metrics_endpoint = next(endpoint for endpoint in spec.endpoints if endpoint.name == "metrics")
    assert metrics_endpoint.weight == 10
