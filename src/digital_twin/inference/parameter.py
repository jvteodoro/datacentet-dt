from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParameterVector:
    values: tuple[float, ...]
    covariance: tuple[tuple[float, ...], ...] | None
    timestamp: int
    strategy_id: str
