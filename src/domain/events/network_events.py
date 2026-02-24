from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real

from .base_event import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True, eq=False, repr=False)
class WorkloadSubmittedEvent(DomainEvent):
    workload_id: str
    source: str
    destination: str
    payload_size: float
    required_cycles: float | None = None

    def __post_init__(self) -> None:
        DomainEvent.__post_init__(self)
        payload_size = _validate_non_negative_scalar(self.payload_size, "payload_size")
        required_cycles = 1.0 if self.required_cycles is None else self.required_cycles

        object.__setattr__(self, "payload_size", payload_size)
        object.__setattr__(self, "required_cycles", _validate_non_negative_scalar(required_cycles, "required_cycles"))

    def _event_marker(self) -> None:
        return None


@dataclass(frozen=True, slots=True, kw_only=True, eq=False, repr=False)
class WorkloadDeliveredEvent(DomainEvent):
    workload_id: str
    source: str
    destination: str
    required_cycles: float

    def __post_init__(self) -> None:
        DomainEvent.__post_init__(self)
        object.__setattr__(self, "required_cycles", _validate_non_negative_scalar(self.required_cycles, "required_cycles"))

    def _event_marker(self) -> None:
        return None


def _validate_non_negative_scalar(value: float, field_name: str) -> float:
    if not isinstance(value, Real):
        raise TypeError(f"{field_name} must be a real scalar")

    numeric_value = float(value)
    if not isfinite(numeric_value):
        raise ValueError(f"{field_name} must be finite")

    if numeric_value < 0:
        raise ValueError(f"{field_name} must be non-negative")

    return numeric_value
