from __future__ import annotations

import csv
from pathlib import Path


def parse_locust_stats(path: str | Path) -> dict[str, float]:
    p = Path(path)
    if not p.exists():
        return {"rps": 0.0, "p95": 0.0, "p99": 0.0, "error_rate": 0.0}

    total_row = None
    with p.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("Name") == "Aggregated" or row.get("Type") == "Aggregated":
                total_row = row
    if not total_row:
        return {"rps": 0.0, "p95": 0.0, "p99": 0.0, "error_rate": 0.0}

    requests = float(total_row.get("Request Count", 0) or 0)
    failures = float(total_row.get("Failure Count", 0) or 0)
    return {
        "rps": float(total_row.get("Requests/s", 0) or 0),
        "p95": float(total_row.get("95%", 0) or 0),
        "p99": float(total_row.get("99%", 0) or 0),
        "error_rate": (failures / requests) if requests > 0 else 0.0,
    }
