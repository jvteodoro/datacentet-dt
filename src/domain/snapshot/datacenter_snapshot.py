from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple


@dataclass(frozen=True, slots=True)
class DataCenterSnapshot:
    network_snapshot: Mapping[str, float]
    computational_snapshot: Mapping[str, object]
    total_tasks_completed: int
    total_cycles_processed: float
    total_arrived: float
    total_served: float
    total_dropped: float
    backlog_total: float

    @staticmethod
    def build(
        *,
        network_snapshot: Mapping[str, float],
        computational_snapshot: Mapping[str, object],
    ) -> DataCenterSnapshot:
        immutable_network = MappingProxyType(dict(network_snapshot))
        immutable_compute = MappingProxyType(dict(computational_snapshot))

        total_tasks_completed = int(immutable_compute["completed_tasks_count"])
        total_cycles_processed = float(immutable_compute["consumed_cycles"])
        total_arrived = float(immutable_network["total_arrived"])
        total_served = float(immutable_network["total_served"])
        total_dropped = float(immutable_network["total_dropped"])
        backlog_total = float(immutable_network["current_depth"]) + float(immutable_compute["pending_cycles"])

        return DataCenterSnapshot(
            network_snapshot=immutable_network,
            computational_snapshot=immutable_compute,
            total_tasks_completed=total_tasks_completed,
            total_cycles_processed=total_cycles_processed,
            total_arrived=total_arrived,
            total_served=total_served,
            total_dropped=total_dropped,
            backlog_total=backlog_total,
        )


def build_computational_snapshot(
    *,
    node_id: str,
    current_timestamp: float,
    consumed_cycles: float,
    active_tasks: Tuple[Tuple[str, float], ...],
    completed_tasks: Tuple[str, ...],
) -> Mapping[str, object]:
    pending_cycles = sum(required_cycles for _, required_cycles in active_tasks)
    return MappingProxyType(
        {
            "node_id": node_id,
            "current_timestamp": float(current_timestamp),
            "consumed_cycles": float(consumed_cycles),
            "active_tasks": active_tasks,
            "active_tasks_count": len(active_tasks),
            "completed_tasks": completed_tasks,
            "completed_tasks_count": len(completed_tasks),
            "pending_cycles": float(pending_cycles),
        }
    )


def build_network_snapshot(
    *,
    capacity: float,
    service_rate: float,
    current_depth: float,
    last_event_timestamp: float,
    total_arrived: float,
    total_served: float,
    total_dropped: float,
) -> Mapping[str, float]:
    return MappingProxyType(
        {
            "capacity": float(capacity),
            "service_rate": float(service_rate),
            "current_depth": float(current_depth),
            "last_event_timestamp": float(last_event_timestamp),
            "total_arrived": float(total_arrived),
            "total_served": float(total_served),
            "total_dropped": float(total_dropped),
        }
    )
