from __future__ import annotations

import argparse
from pathlib import Path

from load_testing.analysis.parse_locust_csv import parse_locust_stats
from load_testing.analysis.parse_resource_csv import parse_resource_usage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    derived = run_dir / "derived"
    derived.mkdir(parents=True, exist_ok=True)

    locust = parse_locust_stats(run_dir / "locust_stats.csv")
    resource = parse_resource_usage(run_dir / "resource_usage.csv")

    summary = derived / "summary.md"
    summary.write_text(
        "\n".join(
            [
                "# Run summary",
                f"- rps: {locust['rps']:.3f}",
                f"- p95_ms: {locust['p95']:.3f}",
                f"- p99_ms: {locust['p99']:.3f}",
                f"- error_rate: {locust['error_rate']:.6f}",
                f"- avg_cpu_percent: {resource['avg_cpu']:.3f}",
                f"- peak_rss_bytes: {resource['peak_rss']:.0f}",
                f"- read_delta_bytes: {resource['read_delta']:.0f}",
                f"- write_delta_bytes: {resource['write_delta']:.0f}",
            ]
        ),
        encoding="utf-8",
    )

    bottleneck = derived / "bottleneck.md"
    bottleneck.write_text(
        "\n".join(
            [
                "# Bottleneck attribution",
                "- Use `load_testing/analysis/compare_http_vs_kafka.py` for cross-transport narratives.",
            ]
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
