from __future__ import annotations

from domain.event_bus import InternalEventBus
from domain.events import WorkloadDeliveredEvent, WorkloadSubmittedEvent
from domain.network import NetworkLayer, QueueState


def test_network_layer_delivers_workload_after_deterministic_service_tick() -> None:
    event_bus = InternalEventBus()
    queue = QueueState(capacity=10.0, service_rate=2.0)
    _layer = NetworkLayer(event_bus=event_bus, queue=queue)
    delivered_events: list[WorkloadDeliveredEvent] = []

    def on_delivered(event: WorkloadDeliveredEvent) -> None:
        delivered_events.append(event)

    event_bus.subscribe(WorkloadDeliveredEvent, on_delivered)

    event_bus.publish(
        WorkloadSubmittedEvent(
            workload_id="wl-1",
            source="ingress",
            destination="egress",
            payload_size=4.0,
            required_cycles=10.0,
            timestamp=1.0,
        )
    )

    assert len(delivered_events) == 1
    assert delivered_events[0].workload_id == "wl-1"
    assert delivered_events[0].source == "ingress"
    assert delivered_events[0].destination == "egress"
    assert delivered_events[0].timestamp == 3.0

    assert queue.total_arrived == 4.0
    assert queue.total_served == 4.0
    assert queue.total_dropped == 0.0
    assert queue.current_depth == 0.0


def test_network_layer_preserves_flow_conservation_with_drops() -> None:
    event_bus = InternalEventBus()
    queue = QueueState(capacity=5.0, service_rate=1.0)
    _layer = NetworkLayer(event_bus=event_bus, queue=queue)
    delivered_events: list[WorkloadDeliveredEvent] = []

    def on_delivered(event: WorkloadDeliveredEvent) -> None:
        delivered_events.append(event)

    event_bus.subscribe(WorkloadDeliveredEvent, on_delivered)

    event_bus.publish(
        WorkloadSubmittedEvent(
            workload_id="wl-2",
            source="src",
            destination="dst",
            payload_size=9.0,
            required_cycles=7.0,
            timestamp=2.0,
        )
    )

    assert len(delivered_events) == 1
    assert delivered_events[0].timestamp == 7.0

    assert queue.total_arrived == 9.0
    assert queue.total_served == 5.0
    assert queue.total_dropped == 4.0
    assert queue.current_depth == 0.0
    assert queue.total_arrived == queue.total_served + queue.total_dropped + queue.current_depth
