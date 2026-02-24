from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from numbers import Real

from domain.event_bus import InternalEventBus
from domain.events import TaskCompletedEvent, TaskStartedEvent, WorkloadDeliveredEvent


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


@dataclass(slots=True)
class TaskState:
    task_id: str
    workload_id: str
    start_timestamp: float
    required_cycles: float
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id must be non-empty")
        if not self.workload_id:
            raise ValueError("workload_id must be non-empty")
        self.start_timestamp = _validate_timestamp(self.start_timestamp)
        self.required_cycles = _validate_non_negative_scalar(
            self.required_cycles,
            "required_cycles",
        )


@dataclass(slots=True)
class ComputeNode:
    node_id: str
    cycles_per_time_unit: float
    consumed_cycles: float = 0.0
    current_timestamp: float = 0.0
    active_tasks: list[TaskState] = field(default_factory=list)
    completed_tasks: list[TaskState] = field(default_factory=list)
    _task_progress: dict[str, float] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must be non-empty")
        self.cycles_per_time_unit = _validate_non_negative_scalar(
            self.cycles_per_time_unit,
            "cycles_per_time_unit",
            strictly_positive=True,
        )
        self.consumed_cycles = _validate_non_negative_scalar(self.consumed_cycles, "consumed_cycles")
        self.current_timestamp = _validate_timestamp(self.current_timestamp)

    def start_task(self, task: TaskState, timestamp: float) -> None:
        start_timestamp = _validate_timestamp(timestamp)
        if start_timestamp < self.current_timestamp:
            raise ValueError("timestamp violates temporal causality")

        self.advance_to(start_timestamp)

        if task.task_id in self._task_progress:
            raise ValueError("task_id already registered")

        task.start_timestamp = start_timestamp
        task.status = TaskStatus.RUNNING
        self.active_tasks.append(task)
        self._task_progress[task.task_id] = 0.0

    def advance_to(self, timestamp: float) -> list[tuple[TaskState, float]]:
        target_timestamp = _validate_timestamp(timestamp)
        if target_timestamp < self.current_timestamp:
            raise ValueError("timestamp violates temporal causality")

        completed_in_window: list[tuple[TaskState, float]] = []
        remaining_cycles = (target_timestamp - self.current_timestamp) * self.cycles_per_time_unit

        while remaining_cycles > 0.0 and self.active_tasks:
            task = self.active_tasks[0]
            progressed = self._task_progress[task.task_id]
            pending_cycles = task.required_cycles - progressed

            if remaining_cycles >= pending_cycles:
                completion_delta = pending_cycles / self.cycles_per_time_unit
                self.current_timestamp += completion_delta
                self.consumed_cycles += pending_cycles
                remaining_cycles -= pending_cycles

                self._task_progress.pop(task.task_id, None)
                self.active_tasks.pop(0)
                task.status = TaskStatus.COMPLETED
                self.completed_tasks.append(task)
                completed_in_window.append((task, self.current_timestamp))
                continue

            self._task_progress[task.task_id] = progressed + remaining_cycles
            self.consumed_cycles += remaining_cycles
            self.current_timestamp = target_timestamp
            remaining_cycles = 0.0

        if not self.active_tasks:
            self.current_timestamp = target_timestamp

        return completed_in_window


class ComputationalLayer:
    def __init__(self, event_bus: InternalEventBus, compute_node: ComputeNode) -> None:
        self._event_bus = event_bus
        self._compute_node = compute_node
        self._event_bus.subscribe(WorkloadDeliveredEvent, self._handle_workload_delivered)

    def _handle_workload_delivered(self, event: WorkloadDeliveredEvent) -> None:
        start_timestamp = max(self._compute_node.current_timestamp, float(event.timestamp))
        task = TaskState(
            task_id=f"task::{event.workload_id}",
            workload_id=event.workload_id,
            start_timestamp=start_timestamp,
            required_cycles=event.required_cycles,
        )
        self._compute_node.start_task(task, start_timestamp)

        self._event_bus.publish(
            TaskStartedEvent(
                task_id=task.task_id,
                node_id=self._compute_node.node_id,
                timestamp=start_timestamp,
            )
        )

        completion_events = self._compute_node.advance_to(
            start_timestamp + (task.required_cycles / self._compute_node.cycles_per_time_unit),
        )
        for completed_task, completion_timestamp in completion_events:
            self._event_bus.publish(
                TaskCompletedEvent(
                    task_id=completed_task.task_id,
                    node_id=self._compute_node.node_id,
                    timestamp=completion_timestamp,
                )
            )


def _validate_non_negative_scalar(
    value: float,
    field_name: str,
    strictly_positive: bool = False,
) -> float:
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


def _validate_timestamp(timestamp: float) -> float:
    if not isinstance(timestamp, Real):
        raise TypeError("timestamp must be a real scalar")

    numeric_value = float(timestamp)
    if not isfinite(numeric_value):
        raise ValueError("timestamp must be finite")

    return numeric_value
