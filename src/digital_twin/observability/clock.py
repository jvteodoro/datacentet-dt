from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol
from time import monotonic


class Clock(Protocol):
    def now_monotonic(self) -> float:
        ...

    def now_utc_rfc3339(self) -> str:
        ...


class DefaultClock:
    def now_monotonic(self) -> float:
        return monotonic()

    def now_utc_rfc3339(self) -> str:
        return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")
