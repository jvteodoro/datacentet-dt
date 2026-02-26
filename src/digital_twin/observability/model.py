from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class MetricKind(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


MetricValue = int | float | Mapping[str, int | float]


@dataclass(frozen=True, slots=True)
class MetricPoint:
    kind: MetricKind
    value: MetricValue
    labels: Mapping[str, str] = field(default_factory=dict)
    unit: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "kind": self.kind.value,
            "value": self.value,
            "labels": dict(sorted(self.labels.items())),
            "unit": self.unit,
            "description": self.description,
        }
        return payload


@dataclass(frozen=True, slots=True)
class MetricsSnapshot:
    timestamp_utc: str
    mode: str
    metrics: Mapping[str, MetricPoint]
    node_id: str | None = None
    produced_at_utc: str | None = None
    snapshot_age_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        ordered_metrics = {
            metric_name: point.to_dict()
            for metric_name, point in sorted(self.metrics.items(), key=lambda item: item[0])
        }
        return {
            "timestamp_utc": self.timestamp_utc,
            "produced_at_utc": self.produced_at_utc,
            "snapshot_age_ms": self.snapshot_age_ms,
            "node_id": self.node_id,
            "mode": self.mode,
            "metrics": ordered_metrics,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)
