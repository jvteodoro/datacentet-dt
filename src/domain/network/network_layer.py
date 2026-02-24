from __future__ import annotations

from domain.event_bus import InternalEventBus
from domain.events import WorkloadDeliveredEvent, WorkloadSubmittedEvent

from .queue_state import QueueState


class NetworkLayer:
    def __init__(self, event_bus: InternalEventBus, queue: QueueState) -> None:
        self._event_bus: InternalEventBus = event_bus
        self._queue: QueueState = queue
        self._last_delivery_timestamp: float = float(queue.last_event_timestamp)
        self.register_handlers()

    def register_handlers(self) -> None:
        self._event_bus.subscribe(WorkloadSubmittedEvent, self._handle_workload_submitted)

    def _handle_workload_submitted(self, event: WorkloadSubmittedEvent) -> None:
        self._queue.apply_arrival(amount=event.payload_size, timestamp=event.timestamp)

        if self._queue.current_depth > 0.0:
            delivery_timestamp = max(
                event.timestamp,
                self._queue.last_event_timestamp,
                self._last_delivery_timestamp,
            ) + (self._queue.current_depth / self._queue.service_rate)
            self._queue.apply_arrival(amount=0.0, timestamp=delivery_timestamp)

        if self._queue.current_depth == 0.0:
            delivered_at = max(event.timestamp, self._queue.last_event_timestamp, self._last_delivery_timestamp)
            self._last_delivery_timestamp = delivered_at
            self._event_bus.publish(
                WorkloadDeliveredEvent(
                    workload_id=event.workload_id,
                    source=event.source,
                    destination=event.destination,
                    timestamp=delivered_at,
                )
            )
