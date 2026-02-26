from __future__ import annotations

import csv
from pathlib import Path


def _f(row: dict[str, str], key: str) -> float:
    v = row.get(key, "")
    if v in (None, ""):
        return 0.0
    return float(v)


def parse_resource_usage(path: str | Path) -> dict[str, float]:
    p = Path(path)
    if not p.exists():
        return {"avg_cpu": 0.0, "peak_rss": 0.0, "read_delta": 0.0, "write_delta": 0.0}

    rows = []
    with p.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return {"avg_cpu": 0.0, "peak_rss": 0.0, "read_delta": 0.0, "write_delta": 0.0}

    cpus = [_f(r, "cpu_percent") for r in rows]
    rss = [_f(r, "rss_bytes") for r in rows]
    read_b = [_f(r, "read_bytes_total") for r in rows]
    write_b = [_f(r, "write_bytes_total") for r in rows]
    return {
        "avg_cpu": sum(cpus) / len(cpus),
        "peak_rss": max(rss),
        "read_delta": max(read_b) - min(read_b),
        "write_delta": max(write_b) - min(write_b),
    }
