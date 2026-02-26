from __future__ import annotations

import argparse
from pathlib import Path

from load_testing.analysis.parse_locust_csv import parse_locust_stats
from load_testing.analysis.parse_resource_csv import parse_resource_usage


def _narrative(http: dict[str, float], kafka: dict[str, float]) -> str:
    if http["avg_cpu"] > 85 and kafka["avg_cpu"] > 85 and kafka["write_delta"] < 1e6:
        return "Domain bottleneck likely (CPU saturation with low DB IO)."
    if kafka["write_delta"] > http["write_delta"] * 1.5 and kafka["p99"] > http["p99"]:
        return "DB bottleneck likely (higher DB IO with latency increase)."
    if kafka["rps"] < http["rps"] and kafka["avg_cpu"] < http["avg_cpu"]:
        return "Transport/consumer bottleneck likely in Kafka path (throughput drops without CPU saturation)."
    if http["p99"] > kafka["p99"] and http["avg_cpu"] < 60:
        return "Transport/HTTP bottleneck likely (high p99 with low CPU)."
    return "Mixed bottleneck signature; inspect lag, DB metrics, and per-endpoint distributions."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--http-run", required=True)
    parser.add_argument("--kafka-run", required=True)
    args = parser.parse_args()

    http_run = Path(args.http_run)
    kafka_run = Path(args.kafka_run)
    http = parse_locust_stats(http_run / "locust_stats.csv") | parse_resource_usage(http_run / "resource_usage.csv")
    kafka = parse_locust_stats(kafka_run / "locust_stats.csv") | parse_resource_usage(kafka_run / "resource_usage.csv")

    out = kafka_run / "derived" / "http_vs_kafka.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "\n".join(
            [
                "# HTTP vs Kafka comparison",
                "| metric | http | kafka |",
                "|---|---:|---:|",
                f"| rps | {http['rps']:.3f} | {kafka['rps']:.3f} |",
                f"| p95_ms | {http['p95']:.3f} | {kafka['p95']:.3f} |",
                f"| p99_ms | {http['p99']:.3f} | {kafka['p99']:.3f} |",
                f"| error_rate | {http['error_rate']:.6f} | {kafka['error_rate']:.6f} |",
                f"| avg_cpu_percent | {http['avg_cpu']:.3f} | {kafka['avg_cpu']:.3f} |",
                f"| peak_rss_bytes | {http['peak_rss']:.0f} | {kafka['peak_rss']:.0f} |",
                "",
                "## Bottleneck attribution",
                f"- {_narrative(http, kafka)}",
            ]
        ),
        encoding="utf-8",
    )
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
