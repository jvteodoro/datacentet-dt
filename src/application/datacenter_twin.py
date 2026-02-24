from __future__ import annotations

from domain.compute import ComputationalLayer, ComputeNode
from domain.event_bus import InternalEventBus
from domain.events import DomainEvent
from domain.network import NetworkLayer, QueueState
from domain.snapshot.datacenter_snapshot import (
    DataCenterSnapshot,
    build_computational_snapshot,
    build_network_snapshot,
)


class DataCenterTwin:
    def __init__(
        self,
        *,
        queue_capacity: float = 10.0,
        queue_service_rate: float = 2.0,
        compute_node_id: str = "node-A",
        cycles_per_time_unit: float = 4.0,
    ) -> None:
        self._event_bus = InternalEventBus()
        self._network_queue = QueueState(capacity=queue_capacity, service_rate=queue_service_rate)
        self._compute_node = ComputeNode(node_id=compute_node_id, cycles_per_time_unit=cycles_per_time_unit)

        self._network_layer = NetworkLayer(event_bus=self._event_bus, queue=self._network_queue)
        self._computational_layer = ComputationalLayer(event_bus=self._event_bus, compute_node=self._compute_node)

    def ingest_event(self, event: DomainEvent) -> None:
        self._event_bus.publish(event)

    def get_snapshot(self) -> DataCenterSnapshot:
        network_snapshot = build_network_snapshot(
            capacity=self._network_queue.capacity,
            service_rate=self._network_queue.service_rate,
            current_depth=self._network_queue.current_depth,
            last_event_timestamp=self._network_queue.last_event_timestamp,
            total_arrived=self._network_queue.total_arrived,
            total_served=self._network_queue.total_served,
            total_dropped=self._network_queue.total_dropped,
        )
        computational_snapshot = build_computational_snapshot(
            node_id=self._compute_node.node_id,
            current_timestamp=self._compute_node.current_timestamp,
            consumed_cycles=self._compute_node.consumed_cycles,
            active_tasks=tuple((task.task_id, task.required_cycles) for task in self._compute_node.active_tasks),
            completed_tasks=tuple(task.task_id for task in self._compute_node.completed_tasks),
        )
        return DataCenterSnapshot.build(
            network_snapshot=network_snapshot,
            computational_snapshot=computational_snapshot,
        )
