from __future__ import annotations

from dataclasses import asdict

from domain.compute import ComputationalLayer, ComputeNode
from domain.event_bus import InternalEventBus
from domain.events import (
    TaskCompletedEvent,
    TaskStartedEvent,
    WorkloadDeliveredEvent,
    WorkloadSubmittedEvent,
)
from domain.network import NetworkLayer, QueueState


def _build_integrated_system(
    *,
    capacity: float = 10.0,
    service_rate: float = 2.0,
    cycles_per_time_unit: float = 4.0,
):
    bus = InternalEventBus()
    queue = QueueState(capacity=capacity, service_rate=service_rate)
    node = ComputeNode(node_id="node-A", cycles_per_time_unit=cycles_per_time_unit)

    NetworkLayer(event_bus=bus, queue=queue)
    ComputationalLayer(event_bus=bus, compute_node=node)

    delivered_events: list[WorkloadDeliveredEvent] = []
    started_events: list[TaskStartedEvent] = []
    completed_events: list[TaskCompletedEvent] = []

    bus.subscribe(WorkloadDeliveredEvent, delivered_events.append)
    bus.subscribe(TaskStartedEvent, started_events.append)
    bus.subscribe(TaskCompletedEvent, completed_events.append)

    return bus, queue, node, delivered_events, started_events, completed_events


def test_t1_fluxo_completo_submissao_para_execucao_completa() -> None:
    bus, _queue, _node, delivered, started, completed = _build_integrated_system()

    bus.publish(
        WorkloadSubmittedEvent(
            workload_id="wl-1",
            source="ingress",
            destination="node-A",
            payload_size=4.0,
            timestamp=1.0,
        )
    )

    assert len(delivered) == 1
    assert len(started) == 1
    assert len(completed) == 1

    assert delivered[0].workload_id == "wl-1"
    assert started[0].task_id == "task::wl-1"
    assert completed[0].task_id == "task::wl-1"


def test_t2_causalidade_tarefa_inicia_apos_entrega() -> None:
    bus, _queue, _node, delivered, started, _completed = _build_integrated_system()

    bus.publish(
        WorkloadSubmittedEvent(
            workload_id="wl-causal",
            source="src",
            destination="node-A",
            payload_size=6.0,
            timestamp=2.0,
        )
    )

    assert len(delivered) == 1
    assert len(started) == 1

    workload_delivered = delivered[0]
    task_started = started[0]

    assert task_started.timestamp >= workload_delivered.timestamp


def test_t3_conservacao_fila_e_ciclos_apos_integracao() -> None:
    bus, queue, node, delivered, started, completed = _build_integrated_system(
        capacity=5.0,
        service_rate=1.0,
        cycles_per_time_unit=2.0,
    )

    bus.publish(
        WorkloadSubmittedEvent(
            workload_id="wl-overflow",
            source="src",
            destination="node-A",
            payload_size=9.0,
            timestamp=0.0,
        )
    )

    assert queue.total_arrived == 9.0
    assert queue.total_served == 5.0
    assert queue.total_dropped == 4.0
    assert queue.current_depth == 0.0
    assert queue.total_arrived == queue.total_served + queue.total_dropped + queue.current_depth

    assert len(delivered) == 1
    assert len(started) == 1
    assert len(completed) == 1

    cycles_recebidos = float(len(delivered))
    cycles_consumidos = node.consumed_cycles
    cycles_restantes = sum(task.required_cycles for task in node.active_tasks)

    assert cycles_recebidos == cycles_consumidos + cycles_restantes


def _run_deterministic_sequence() -> dict[str, object]:
    bus, queue, node, delivered, started, completed = _build_integrated_system(
        capacity=10.0,
        service_rate=2.5,
        cycles_per_time_unit=3.0,
    )

    submissions = [
        WorkloadSubmittedEvent(
            workload_id="wl-1",
            source="ingress",
            destination="node-A",
            payload_size=2.0,
            timestamp=1.0,
        ),
        WorkloadSubmittedEvent(
            workload_id="wl-2",
            source="ingress",
            destination="node-A",
            payload_size=5.0,
            timestamp=5.0,
        ),
        WorkloadSubmittedEvent(
            workload_id="wl-3",
            source="ingress",
            destination="node-A",
            payload_size=3.0,
            timestamp=9.0,
        ),
    ]

    for event in submissions:
        bus.publish(event)

    return {
        "queue": {
            "capacity": queue.capacity,
            "service_rate": queue.service_rate,
            "current_depth": queue.current_depth,
            "last_event_timestamp": queue.last_event_timestamp,
            "total_arrived": queue.total_arrived,
            "total_served": queue.total_served,
            "total_dropped": queue.total_dropped,
        },
        "compute": {
            "node_id": node.node_id,
            "cycles_per_time_unit": node.cycles_per_time_unit,
            "consumed_cycles": node.consumed_cycles,
            "current_timestamp": node.current_timestamp,
            "active_tasks": [task.task_id for task in node.active_tasks],
            "completed_tasks": [task.task_id for task in node.completed_tasks],
        },
        "events": {
            "delivered": [_event_payload(event) for event in delivered],
            "started": [_event_payload(event) for event in started],
            "completed": [_event_payload(event) for event in completed],
        },
    }


def _event_payload(event: object) -> dict[str, object]:
    payload = asdict(event)
    payload.pop("event_id", None)
    return payload


def test_t4_determinismo_composto_rede_computacao_eventos() -> None:
    primeira_execucao = _run_deterministic_sequence()
    segunda_execucao = _run_deterministic_sequence()

    assert primeira_execucao == segunda_execucao
