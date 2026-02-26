from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import NAMESPACE_URL, uuid5


@dataclass(frozen=True, slots=True)
class GeneratorProfile:
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
    hot_stream_probability: float = 0.0


@dataclass(frozen=True, slots=True)
class InfraSize:
    num_nodes: int
    num_links: int
    num_servers: int


class SeededTelemetryGenerator:
    """Deterministic logical event stream generator shared by HTTP and Kafka load suites."""

    def __init__(
        self,
        *,
        profile: GeneratorProfile,
        infra_size: InfraSize,
        seed: int,
        source: str,
        require_ingest_id: bool = True,
        duplicate_rate: float = 0.0,
    ) -> None:
        self.profile = profile
        self.infra_size = infra_size
        self.seed = seed
        self.source = source
        self.require_ingest_id = require_ingest_id
        self.duplicate_rate = max(0.0, min(duplicate_rate, 1.0))
        self._rng = random.Random(seed)
        self._logical_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self._global_counter = 0
        self._stream_counters: dict[str, int] = {}
        self._last_message_by_stream: dict[str, dict[str, Any]] = {}

    def next_interarrival_seconds(self) -> float:
        return self._rng.expovariate(max(self.profile.lambda_rate, 1e-9))

    def next_message(self) -> dict[str, Any]:
        stream_id = self._pick_stream_id()
        if self.duplicate_rate > 0 and stream_id in self._last_message_by_stream and self._rng.random() < self.duplicate_rate:
            duplicated = dict(self._last_message_by_stream[stream_id])
            duplicated["source_time_utc"] = self._advance_time()
            return duplicated

        event_type = self._pick_event_type()
        stream_counter = self._stream_counters.get(stream_id, 0)
        self._stream_counters[stream_id] = stream_counter + 1

        message = {
            "stream_id": stream_id,
            "source": self.source,
            "source_time_utc": self._advance_time(),
            "event_type": event_type,
            "payload": self._build_payload(stream_id, stream_counter, event_type),
            "metadata": {
                "sequence": stream_counter,
                "generator_seed": self.seed,
                "infra_size": {
                    "num_nodes": self.infra_size.num_nodes,
                    "num_links": self.infra_size.num_links,
                    "num_servers": self.infra_size.num_servers,
                },
            },
        }
        if self.require_ingest_id:
            message["ingest_id"] = str(uuid5(NAMESPACE_URL, f"{self.seed}:{stream_id}:{stream_counter}:{event_type}"))

        self._global_counter += 1
        self._last_message_by_stream[stream_id] = message
        return message

    def _advance_time(self) -> str:
        self._logical_time += timedelta(seconds=self.next_interarrival_seconds())
        return self._logical_time.isoformat().replace("+00:00", "Z")

    def _pick_stream_id(self) -> str:
        if self.profile.hot_stream_probability > 0 and self._rng.random() < self.profile.hot_stream_probability:
            return "dc1"
        return f"dc{1 + self._rng.randrange(0, max(self.profile.stream_count, 1))}"

    def _pick_event_type(self) -> str:
        weighted = [
            ("WorkloadStarted", self.profile.workload_weight),
            ("Tick", self.profile.tick_weight),
            ("FlowStarted", self.profile.flow_weight),
            ("FlowEnded", max(1, self.profile.flow_weight // 2)),
            ("WorkloadEnded", max(1, self.profile.workload_weight // 2)),
        ]
        table = [name for name, weight in weighted for _ in range(max(weight, 0))]
        return table[self._rng.randrange(0, len(table))]

    def _build_payload(self, stream_id: str, sequence: int, event_type: str) -> dict[str, Any]:
        if event_type == "Tick":
            return {
                "delta_time": round(max(0.01, min(3.0, self._rng.lognormvariate(self.profile.lognormal_mu, self.profile.lognormal_sigma))), 6),
                "active_nodes_hint": min(self.infra_size.num_nodes, 1 + (sequence % max(1, self.infra_size.num_nodes))),
            }
        if event_type in {"WorkloadStarted", "WorkloadEnded"}:
            workload_id = f"{stream_id}-wl-{sequence}"
            if event_type == "WorkloadEnded":
                return {"workload_id": workload_id}
            return {
                "workload_id": workload_id,
                "server_id": f"srv-{1 + self._rng.randrange(0, max(1, self.infra_size.num_servers))}",
                "cpu_demand": round(max(0.1, self._rng.lognormvariate(0.1, 0.2)), 6),
                "memory_demand": round(max(0.1, self._rng.lognormvariate(0.2, 0.25)), 6),
                "remaining_size": round(max(0.01, self._pareto(scale=1.0, alpha=self.profile.pareto_alpha)), 6),
            }
        flow_id = f"{stream_id}-flow-{sequence}"
        if event_type == "FlowEnded":
            return {"flow_id": flow_id}
        src = f"n-{1 + self._rng.randrange(0, max(1, self.infra_size.num_nodes))}"
        dst = f"n-{1 + self._rng.randrange(0, max(1, self.infra_size.num_nodes))}"
        return {
            "flow_id": flow_id,
            "src": src,
            "dst": dst,
            "path": [src, dst],
            "rate": round(max(0.1, self._rng.lognormvariate(0.0, 0.25)), 6),
            "size": round(max(0.01, self._pareto(scale=0.5, alpha=self.profile.pareto_alpha)), 6),
        }

    def _pareto(self, *, scale: float, alpha: float) -> float:
        u = max(self._rng.random(), 1e-12)
        return scale * (1.0 / (u ** (1.0 / max(alpha, 1e-9))))
