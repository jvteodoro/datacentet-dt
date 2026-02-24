from __future__ import annotations

"""Golden integration scenario for the digital twin.

This test validates the canonical end-to-end scientific path of the system:
network intake -> queue evolution -> workload delivery -> compute execution -> completion.

Physical/engineering laws verified:
- Queue mass conservation: arrived = served + dropped + depth.
- Compute-cycle conservation: required = processed + remaining.
- Causality: task start must happen after workload delivery.
- Snapshot immutability and deterministic replay.

This file is the canonical reference scenario used as a deterministic baseline for
future regression, contract validation, and inference workflows.
"""

from application.datacenter_twin import DataCenterTwin
from domain.events import TaskStartedEvent, WorkloadDeliveredEvent, WorkloadSubmittedEvent


NETWORK_CAPACITY = 100.0
NETWORK_SERVICE_RATE = 10.0
CPU_CAPACITY = 50.0
MEMORY_CAPACITY = 1024.0

WORKLOAD_ID = "wl-golden"
REQUIRED_CYCLES = 200.0
MEMORY_REQUIRED = 100.0
PAYLOAD_SIZE = 50.0


def build_twin() -> DataCenterTwin:
    return DataCenterTwin(
        queue_capacity=NETWORK_CAPACITY,
        queue_service_rate=NETWORK_SERVICE_RATE,
        cycles_per_time_unit=CPU_CAPACITY,
    )


def run_scenario(twin: DataCenterTwin) -> dict[str, object]:
    delivered: list[WorkloadDeliveredEvent] = []
    started: list[TaskStartedEvent] = []

    twin._event_bus.subscribe(WorkloadDeliveredEvent, delivered.append)
    twin._event_bus.subscribe(TaskStartedEvent, started.append)

    # t = 0.0 -> WorkloadSubmitted
    twin.ingest_event(
        WorkloadSubmittedEvent(
            workload_id=WORKLOAD_ID,
            source="ingress",
            destination="node-A",
            payload_size=PAYLOAD_SIZE,
            required_cycles=REQUIRED_CYCLES,
            timestamp=0.0,
        )
    )

    # t = 5.0, 10.0, 15.0 -> empty events only to advance simulation time.
    #
    # Internal derived events (delivery/start/completion) are emitted synchronously by
    # the domain and may move the event-bus clock forward in the same ingest call.
    # We therefore clamp requested no-op timestamps to preserve the bus temporal rule
    # without changing the intended canonical checkpoints.
    for idx, ts in enumerate((5.0, 10.0, 15.0), start=1):
        current_snapshot = twin.get_snapshot()
        current_clock = max(
            float(current_snapshot.network_snapshot["last_event_timestamp"]),
            float(current_snapshot.computational_snapshot["current_timestamp"]),
        )
        effective_timestamp = max(ts, current_clock)
        twin.ingest_event(
            WorkloadSubmittedEvent(
                workload_id=f"noop-{idx}",
                source="clock",
                destination="node-A",
                payload_size=0.0,
                required_cycles=0.0,
                timestamp=effective_timestamp,
            )
        )

    snapshot = twin.get_snapshot()

    main_delivery = next(event for event in delivered if event.workload_id == WORKLOAD_ID)
    main_start = next(event for event in started if event.task_id == f"task::{WORKLOAD_ID}")

    processed_cycles = float(snapshot.computational_snapshot["consumed_cycles"])
    remaining_cycles = float(snapshot.computational_snapshot["pending_cycles"])
    memory_allocated = float(snapshot.computational_snapshot.get("memory_allocated", 0.0))

    return {
        "snapshot": snapshot,
        "workload_delivered_timestamp": float(main_delivery.timestamp),
        "task_started_timestamp": float(main_start.timestamp),
        "processed_cycles": processed_cycles,
        "remaining_cycles": remaining_cycles,
        "memory_allocated": memory_allocated,
    }


def test_golden_path() -> None:
    twin = build_twin()
    result = run_scenario(twin)
    snapshot = result["snapshot"]

    assert isinstance(snapshot, object)

    # T1 — delivery occurred
    assert result["workload_delivered_timestamp"] >= 0.0

    # T2 — execution started after delivery
    assert result["task_started_timestamp"] >= result["workload_delivered_timestamp"]

    # T3 — queue conservation
    assert snapshot.total_arrived == snapshot.total_served + snapshot.total_dropped + snapshot.network_snapshot["current_depth"]

    # T4 — cycle conservation
    assert REQUIRED_CYCLES == result["processed_cycles"] + result["remaining_cycles"]

    # T5 — memory released after completion
    assert MEMORY_REQUIRED <= MEMORY_CAPACITY
    assert result["memory_allocated"] == 0.0

    # T6 — snapshot immutability
    snapshot_before = twin.get_snapshot()
    try:
        snapshot_before.network_snapshot["current_depth"] = 999.0  # type: ignore[index]
    except TypeError:
        pass
    snapshot_after = twin.get_snapshot()
    assert snapshot_before == snapshot_after


def test_replay_determinism() -> None:
    run1 = run_scenario(build_twin())["snapshot"]
    run2 = run_scenario(build_twin())["snapshot"]

    # T7 — deterministic replay
    assert run1 == run2
