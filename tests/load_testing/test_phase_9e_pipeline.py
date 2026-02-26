from __future__ import annotations

import csv
from pathlib import Path

from load_testing.analysis.parse_resource_csv import parse_resource_usage
from load_testing.campaigns.manifest import build_manifest
from load_testing.locust_ingest.profiles import build_profile_spec
from load_testing.locust_ingest.seeded_generator import InfraSize, SeededTelemetryGenerator


def test_seeded_generator_determinism_per_stream() -> None:
    profile = build_profile_spec("mixed_with_flows")
    g1 = SeededTelemetryGenerator(profile=profile, infra_size=InfraSize(10, 20, 5), seed=7, source="t")
    g2 = SeededTelemetryGenerator(profile=profile, infra_size=InfraSize(10, 20, 5), seed=7, source="t")

    events1 = [g1.next_message() for _ in range(80)]
    events2 = [g2.next_message() for _ in range(80)]

    assert events1 == events2

    by_stream1 = {}
    by_stream2 = {}
    for e in events1:
        by_stream1.setdefault(e["stream_id"], []).append(e["payload"])
    for e in events2:
        by_stream2.setdefault(e["stream_id"], []).append(e["payload"])
    assert by_stream1 == by_stream2


def test_parse_resource_csv_handles_missing_optional_columns(tmp_path: Path) -> None:
    path = tmp_path / "resource.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["timestamp_utc", "pid", "cpu_percent", "rss_bytes"])
        writer.writeheader()
        writer.writerow({"timestamp_utc": "2026-01-01T00:00:00Z", "pid": "1", "cpu_percent": "50.0", "rss_bytes": "100"})
    parsed = parse_resource_usage(path)
    assert parsed["avg_cpu"] == 50.0
    assert parsed["peak_rss"] == 100.0
    assert parsed["read_delta"] == 0.0
    assert parsed["write_delta"] == 0.0


def test_manifest_has_required_fields_and_stable_ordering() -> None:
    manifest = build_manifest(
        run_id="r1",
        transport="http",
        target="http://127.0.0.1:8091",
        profile="steady_poisson_users",
        seed=42,
        git_sha="abc",
        users=10,
        spawn_rate=2,
    )
    assert list(manifest.keys())[:6] == ["run_id", "transport", "target", "profile", "seed", "git_sha"]
    assert list(manifest.keys())[6:] == ["spawn_rate", "users"]
