from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from domain.events import (
    DomainEvent,
    TaskCompletedEvent,
    TaskStartedEvent,
    WorkloadDeliveredEvent,
    WorkloadSubmittedEvent,
)


def test_L1_domain_event_is_immutable_for_timestamp_and_payload():
    event = TaskStartedEvent(task_id="task-1", node_id="node-A")

    with pytest.raises(FrozenInstanceError):
        event.timestamp = 123.0

    with pytest.raises(FrozenInstanceError):
        event.task_id = "task-2"


def test_L2_domain_events_have_unique_identity_when_event_id_is_not_provided():
    events = [
        TaskStartedEvent(task_id="task-1", node_id="node-A"),
        TaskCompletedEvent(task_id="task-1", node_id="node-A"),
        WorkloadSubmittedEvent(workload_id="wl-1", source="src-1"),
        WorkloadDeliveredEvent(
            workload_id="wl-1",
            source="src-1",
            destination="dst-1",
        ),
    ]

    event_ids = [event.event_id for event in events]

    assert len(event_ids) == len(set(event_ids))


def test_L3_domain_events_can_be_sorted_in_ascending_temporal_order():
    unordered_events = [
        WorkloadSubmittedEvent(workload_id="wl-1", source="src", timestamp=3.0),
        TaskStartedEvent(task_id="task-1", node_id="node-A", timestamp=1.0),
        TaskCompletedEvent(task_id="task-1", node_id="node-A", timestamp=2.0),
    ]

    ordered_events = sorted(unordered_events)

    assert [event.timestamp for event in ordered_events] == [1.0, 2.0, 3.0]


def test_L4_domain_event_equality_is_based_only_on_event_id():
    shared_event_id = uuid4()

    first_event = TaskStartedEvent(
        event_id=shared_event_id,
        timestamp=1.0,
        task_id="task-1",
        node_id="node-A",
    )
    second_event = TaskStartedEvent(
        event_id=shared_event_id,
        timestamp=99.0,
        task_id="task-9",
        node_id="node-Z",
    )
    different_id_event = TaskStartedEvent(
        event_id=uuid4(),
        timestamp=1.0,
        task_id="task-1",
        node_id="node-A",
    )

    assert first_event == second_event
    assert first_event != different_id_event


def test_L5_domain_event_repr_includes_class_name_event_id_and_timestamp():
    event = WorkloadSubmittedEvent(
        event_id=uuid4(),
        timestamp=42.5,
        workload_id="wl-1",
        source="src-1",
    )

    representation = repr(event)

    assert event.__class__.__name__ in representation
    assert str(event.event_id) in representation
    assert str(event.timestamp) in representation


@pytest.mark.parametrize(
    "event",
    [
        TaskStartedEvent(task_id="task-1", node_id="node-A"),
        TaskCompletedEvent(task_id="task-1", node_id="node-A"),
        WorkloadSubmittedEvent(workload_id="wl-1", source="src-1"),
        WorkloadDeliveredEvent(
            workload_id="wl-1",
            source="src-1",
            destination="dst-1",
        ),
    ],
)
def test_domain_event_concrete_classes_are_instances_of_domain_event(event):
    assert isinstance(event, DomainEvent)
