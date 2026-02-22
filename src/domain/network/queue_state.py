from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


@dataclass(slots=True)
class QueueState:
    capacity: float
    service_rate: float
    current_depth: float = 0.0
    last_event_timestamp: float = 0.0
    total_arrived: float = 0.0
    total_served: float = 0.0
    total_dropped: float = 0.0

    def __post_init__(self) -> None:
        self.capacity = self._validated_non_negative_scalar(self.capacity, "capacity", strictly_positive=True)
        self.service_rate = self._validated_non_negative_scalar(
            self.service_rate,
            "service_rate",
            strictly_positive=True,
        )
        self.current_depth = self._validated_non_negative_scalar(self.current_depth, "current_depth")
        self.last_event_timestamp = self._validated_timestamp(self.last_event_timestamp)
        self.total_arrived = self._validated_non_negative_scalar(self.total_arrived, "total_arrived")
        self.total_served = self._validated_non_negative_scalar(self.total_served, "total_served")
        self.total_dropped = self._validated_non_negative_scalar(self.total_dropped, "total_dropped")

        if self.current_depth > self.capacity:
            raise ValueError("current_depth must not exceed capacity")

        self._assert_flow_conservation()

    def apply_arrival(self, amount: float, timestamp: float) -> None:
        arrival_amount = self._validated_non_negative_scalar(amount, "amount")
        next_timestamp = self._validated_timestamp(timestamp)
        self._update_service(next_timestamp)

        available_capacity = self.capacity - self.current_depth
        accepted = min(arrival_amount, available_capacity)
        dropped = arrival_amount - accepted

        self.current_depth += accepted
        self.total_arrived += arrival_amount
        self.total_dropped += dropped
        self.last_event_timestamp = next_timestamp

        self._assert_physical_contracts()

    def _update_service(self, timestamp: float) -> None:
        if timestamp < self.last_event_timestamp:
            raise ValueError("timestamp violates temporal causality")

        delta_t = timestamp - self.last_event_timestamp
        served = min(self.current_depth, self.service_rate * delta_t)

        self.current_depth -= served
        self.total_served += served

        self._assert_physical_contracts()

    def _assert_flow_conservation(self) -> None:
        left = self.total_arrived
        right = self.total_served + self.total_dropped + self.current_depth
        if abs(left - right) > 1e-9:
            raise ValueError("flow conservation contract violated")

    def _assert_physical_contracts(self) -> None:
        if self.current_depth < 0:
            raise ValueError("current_depth must be non-negative")
        if self.total_served < 0:
            raise ValueError("total_served must be non-negative")
        if self.total_dropped < 0:
            raise ValueError("total_dropped must be non-negative")
        if self.current_depth > self.capacity:
            raise ValueError("current_depth must not exceed capacity")

        self._assert_flow_conservation()

    @staticmethod
    def _validated_non_negative_scalar(value: float, field_name: str, strictly_positive: bool = False) -> float:
        if not isinstance(value, Real):
            raise TypeError(f"{field_name} must be a real scalar")

        numeric_value = float(value)
        if not isfinite(numeric_value):
            raise ValueError(f"{field_name} must be finite")

        if strictly_positive and numeric_value <= 0:
            raise ValueError(f"{field_name} must be greater than zero")

        if not strictly_positive and numeric_value < 0:
            raise ValueError(f"{field_name} must be non-negative")

        return numeric_value

    @staticmethod
    def _validated_timestamp(timestamp: float) -> float:
        if not isinstance(timestamp, Real):
            raise TypeError("timestamp must be a real scalar")

        numeric_value = float(timestamp)
        if not isfinite(numeric_value):
            raise ValueError("timestamp must be finite")

        return numeric_value
