from __future__ import annotations

import csv
import os
import signal
import time
from datetime import datetime, timezone

import psutil


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe(value: object) -> str:
    return "" if value is None else str(value)


def sample(pid: int, include_system: bool) -> dict[str, str]:
    proc = psutil.Process(pid)
    info = proc.memory_info()
    row: dict[str, str] = {
        "timestamp_utc": _ts(),
        "pid": str(pid),
        "cpu_percent": _safe(proc.cpu_percent(interval=None)),
        "rss_bytes": _safe(getattr(info, "rss", None)),
        "vms_bytes": _safe(getattr(info, "vms", None)),
        "threads": _safe(proc.num_threads()),
        "open_fds": "",
        "read_bytes_total": "",
        "write_bytes_total": "",
        "system_cpu_percent": "",
        "system_mem_percent": "",
    }
    try:
        row["open_fds"] = _safe(proc.num_fds())
    except Exception:
        pass
    try:
        io = proc.io_counters()
        row["read_bytes_total"] = _safe(getattr(io, "read_bytes", None))
        row["write_bytes_total"] = _safe(getattr(io, "write_bytes", None))
    except Exception:
        pass
    if include_system:
        row["system_cpu_percent"] = _safe(psutil.cpu_percent(interval=None))
        row["system_mem_percent"] = _safe(psutil.virtual_memory().percent)
    return row


def main() -> int:
    target_pid = int(os.environ.get("RESOURCE_PID", "0"))
    out_path = os.environ.get("RESOURCE_CSV", "resource_usage.csv")
    interval = float(os.environ.get("RESOURCE_SAMPLING_INTERVAL_S", "0.5"))
    include_system = os.environ.get("RESOURCE_INCLUDE_SYSTEM", "true").lower() != "false"

    if target_pid <= 0:
        raise SystemExit("RESOURCE_PID must be set to a running process id")

    stop = False

    def _stop_handler(*_: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, _stop_handler)
    signal.signal(signal.SIGINT, _stop_handler)

    fields = [
        "timestamp_utc",
        "pid",
        "cpu_percent",
        "rss_bytes",
        "vms_bytes",
        "threads",
        "open_fds",
        "read_bytes_total",
        "write_bytes_total",
        "system_cpu_percent",
        "system_mem_percent",
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        fh.flush()
        while not stop:
            if not psutil.pid_exists(target_pid):
                break
            try:
                writer.writerow(sample(target_pid, include_system))
                fh.flush()
            except Exception:
                writer.writerow({"timestamp_utc": _ts(), "pid": str(target_pid)})
                fh.flush()
            time.sleep(max(interval, 0.1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
