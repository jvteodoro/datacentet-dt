from __future__ import annotations

from application.datacenter_twin import DataCenterTwin
from domain.events import TaskCompletedEvent, TaskStartedEvent, WorkloadDeliveredEvent, WorkloadSubmittedEvent


def _sequence() -> list[WorkloadSubmittedEvent]:
    return [
        WorkloadSubmittedEvent(
            workload_id="wl-1",
            source="ingress",
            destination="node-A",
            payload_size=4.0,
            required_cycles=8.0,
            timestamp=1.0,
        ),
        WorkloadSubmittedEvent(
            workload_id="wl-2",
            source="ingress",
            destination="node-A",
            payload_size=5.0,
            required_cycles=12.0,
            timestamp=6.0,
        ),
    ]


def test_t1_fluxo_completo_end_to_end() -> None:
    twin = DataCenterTwin(queue_capacity=10.0, queue_service_rate=2.0, cycles_per_time_unit=4.0)

    delivered: list[WorkloadDeliveredEvent] = []
    started: list[TaskStartedEvent] = []
    completed: list[TaskCompletedEvent] = []

    twin._event_bus.subscribe(WorkloadDeliveredEvent, delivered.append)
    twin._event_bus.subscribe(TaskStartedEvent, started.append)
    twin._event_bus.subscribe(TaskCompletedEvent, completed.append)

    twin.ingest_event(
        WorkloadSubmittedEvent(
            workload_id="wl-1",
            source="ingress",
            destination="node-A",
            payload_size=4.0,
            required_cycles=8.0,
            timestamp=1.0,
        )
    )

    snapshot = twin.get_snapshot()

    assert len(delivered) == 1
    assert len(started) == 1
    assert len(completed) == 1
    assert started[0].timestamp >= delivered[0].timestamp
    assert completed[0].timestamp >= started[0].timestamp
    assert snapshot.total_tasks_completed == 1
    assert snapshot.total_arrived == snapshot.total_served + snapshot.total_dropped + snapshot.network_snapshot["current_depth"]


def test_t2_determinismo_global() -> None:
    twin_1 = DataCenterTwin()
    twin_2 = DataCenterTwin()

    for event in _sequence():
        twin_1.ingest_event(event)

    for event in _sequence():
        twin_2.ingest_event(event)

    assert twin_1.get_snapshot() == twin_2.get_snapshot()


def test_t3_snapshot_imutavel_sem_interferencia() -> None:
    twin = DataCenterTwin()
    twin.ingest_event(_sequence()[0])

    snapshot_1 = twin.get_snapshot()

    try:
        snapshot_1.network_snapshot["current_depth"] = 999.0  # type: ignore[index]
    except TypeError:
        pass

    snapshot_2 = twin.get_snapshot()
    assert snapshot_1 == snapshot_2


def test_t4_leis_globais_preservadas() -> None:
    twin = DataCenterTwin(queue_capacity=12.0, queue_service_rate=3.0, cycles_per_time_unit=2.0)

    for event in _sequence():
        twin.ingest_event(event)

    snapshot = twin.get_snapshot()
    net = snapshot.network_snapshot
    comp = snapshot.computational_snapshot

    assert net["total_arrived"] == net["total_served"] + net["total_dropped"] + net["current_depth"]
    assert comp["consumed_cycles"] >= 0.0
    assert snapshot.total_cycles_processed == comp["consumed_cycles"]
    assert snapshot.total_tasks_completed == comp["completed_tasks_count"]
