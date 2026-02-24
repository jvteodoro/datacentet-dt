from __future__ import annotations

import pytest

from domain.compute import ComputationalLayer, ComputeNode, TaskStatus
from domain.event_bus import InternalEventBus
from domain.events import TaskCompletedEvent, TaskStartedEvent, WorkloadDeliveredEvent


def test_t1_workload_delivery_starts_and_completes_task_with_deterministic_time():
    bus = InternalEventBus()
    node = ComputeNode(node_id="node-A", cycles_per_time_unit=5.0)
    ComputationalLayer(event_bus=bus, compute_node=node)

    started_events: list[TaskStartedEvent] = []
    completed_events: list[TaskCompletedEvent] = []

    bus.subscribe(TaskStartedEvent, lambda event: started_events.append(event))
    bus.subscribe(TaskCompletedEvent, lambda event: completed_events.append(event))

    bus.publish(
        WorkloadDeliveredEvent(
            workload_id="wl-1",
            source="src-1",
            destination="node-A",
            required_cycles=10.0,
            timestamp=4.0,
        )
    )

    assert len(started_events) == 1
    assert len(completed_events) == 1
    assert started_events[0].timestamp >= 4.0
    assert completed_events[0].timestamp == pytest.approx(6.0)
    assert node.consumed_cycles == pytest.approx(10.0)
    assert node.current_timestamp == pytest.approx(6.0)


def test_t2_compute_node_tracks_active_and_completed_tasks_consistently():
    node = ComputeNode(node_id="node-A", cycles_per_time_unit=2.0)
    bus = InternalEventBus()
    ComputationalLayer(event_bus=bus, compute_node=node)

    bus.publish(
        WorkloadDeliveredEvent(
            workload_id="wl-1",
            source="src-1",
            destination="node-A",
            required_cycles=3.0,
            timestamp=1.0,
        )
    )

    assert node.active_tasks == []
    assert len(node.completed_tasks) == 1
    assert node.completed_tasks[0].status is TaskStatus.COMPLETED
    assert node.completed_tasks[0].workload_id == "wl-1"


def test_t3_events_preserve_temporal_order_relative_to_delivery_timestamp():
    bus = InternalEventBus()
    node = ComputeNode(node_id="node-A", cycles_per_time_unit=4.0, current_timestamp=5.0)
    ComputationalLayer(event_bus=bus, compute_node=node)

    temporal_trace: list[tuple[str, float]] = []

    bus.subscribe(TaskStartedEvent, lambda event: temporal_trace.append(("started", event.timestamp)))
    bus.subscribe(TaskCompletedEvent, lambda event: temporal_trace.append(("completed", event.timestamp)))

    bus.publish(
        WorkloadDeliveredEvent(
            workload_id="wl-2",
            source="src-1",
            destination="node-A",
            required_cycles=8.0,
            timestamp=3.0,
        )
    )

    assert temporal_trace == [
        ("started", 5.0),
        ("completed", 7.0),
    ]
