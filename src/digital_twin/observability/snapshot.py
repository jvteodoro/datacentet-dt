from __future__ import annotations

from .model import MetricsSnapshot


def snapshot_schema(snapshot: MetricsSnapshot) -> list[dict[str, object]]:
    schema = []
    for name, point in sorted(snapshot.metrics.items(), key=lambda item: item[0]):
        schema.append(
            {
                "name": name,
                "kind": point.kind.value,
                "unit": point.unit,
                "description": point.description,
                "labels": dict(sorted(point.labels.items())),
            }
        )
    return schema


def stream_aggregates(snapshot: MetricsSnapshot) -> dict[str, object]:
    metrics = snapshot.metrics

    outcomes_total: dict[str, int] = {}
    for name, point in metrics.items():
        if not name.startswith("streaming.ingestion_outcome_total."):
            continue
        status = name.rsplit(".", 1)[-1].upper()
        outcomes_total[status] = int(point.value)

    kafka_lag_point = metrics.get("streaming.kafka_lag_last")
    return {
        "active_streams": int(_metric_value(metrics, "streaming.streams_active")),
        "evictions_total": int(_metric_value(metrics, "streaming.evictions_total")),
        "outcomes_total": dict(sorted(outcomes_total.items())),
        "kafka_lag_last": None if kafka_lag_point is None else int(kafka_lag_point.value),
    }


def _metric_value(metrics: dict[str, object], key: str, default: int = 0) -> int | float:
    point = metrics.get(key)
    if point is None:
        return default
    return point.value
