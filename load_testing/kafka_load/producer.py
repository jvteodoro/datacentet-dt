from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from load_testing.kafka_load.profiles import load_profile
from load_testing.kafka_load.seeded_generator import GeneratorProfile, InfraSize, SeededTelemetryGenerator

try:
    from kafka import KafkaProducer  # type: ignore
except Exception:  # pragma: no cover - optional dependency in local runs
    KafkaProducer = None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="uniform_streams")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--topic", default="digital-twin-ingest")
    parser.add_argument("--bootstrap-servers", default="127.0.0.1:9092")
    parser.add_argument("--duration-s", type=int, default=0)
    parser.add_argument("--target-rps", type=int, default=0)
    parser.add_argument("--out-jsonl", default="")
    args = parser.parse_args()

    p = load_profile(args.profile)
    duration_s = args.duration_s or p.duration_s
    target_rps = args.target_rps or p.target_rps

    generator = SeededTelemetryGenerator(
        profile=GeneratorProfile(
            name=p.name,
            stream_count=p.stream_count,
            workload_weight=5,
            flow_weight=3,
            tick_weight=4,
            lambda_rate=max(1.0, float(target_rps) / 10.0),
            pareto_alpha=1.6,
            lognormal_mu=-0.2,
            lognormal_sigma=0.4,
            zipf_theta=1.1,
            hot_stream_probability=p.hot_stream_probability,
        ),
        infra_size=InfraSize(num_nodes=200, num_links=400, num_servers=100),
        seed=args.seed,
        source="kafka_load",
        require_ingest_id=True,
    )

    producer = None
    if KafkaProducer is not None:
        producer = KafkaProducer(
            bootstrap_servers=args.bootstrap_servers,
            key_serializer=lambda x: x.encode("utf-8"),
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
            acks="all",
            linger_ms=5,
        )

    out = Path(args.out_jsonl) if args.out_jsonl else None
    end_at = time.time() + duration_s
    sent = 0
    with out.open("w", encoding="utf-8") if out else open("/dev/null", "w", encoding="utf-8") as fh:
        while time.time() < end_at:
            tick_start = time.time()
            for _ in range(target_rps):
                msg = generator.next_message()
                if producer:
                    producer.send(args.topic, key=msg["stream_id"], value=msg)
                fh.write(json.dumps(msg) + "\n")
                sent += 1
            if producer:
                producer.flush()
            remaining = 1.0 - (time.time() - tick_start)
            if remaining > 0:
                time.sleep(remaining)

    print(json.dumps({"sent": sent, "profile": args.profile, "topic": args.topic}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
