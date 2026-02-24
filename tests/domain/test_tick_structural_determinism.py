from __future__ import annotations

import json
import os
import subprocess
import sys


SCRIPT = r'''
import json
from digital_twin.domain.event import DomainEvent
from digital_twin.domain.twin import DataCenterTwin

twin = DataCenterTwin()
events = [
    DomainEvent(timestamp=1, type="AddNode", payload={"node_id": "A"}),
    DomainEvent(timestamp=2, type="AddNode", payload={"node_id": "B"}),
    DomainEvent(timestamp=3, type="AddNode", payload={"node_id": "C"}),
    DomainEvent(timestamp=4, type="AddLink", payload={"src": "A", "dst": "B", "capacity": 10.0}),
    DomainEvent(timestamp=5, type="AddLink", payload={"src": "B", "dst": "C", "capacity": 8.0}),
    DomainEvent(timestamp=6, type="AddServer", payload={"server_id": "S1", "cpu_capacity": 20.0, "memory_capacity": 30.0}),
    DomainEvent(timestamp=7, type="AddServer", payload={"server_id": "S2", "cpu_capacity": 20.0, "memory_capacity": 30.0}),
    DomainEvent(timestamp=8, type="FlowStarted", payload={"flow_id": "F1", "src": "A", "dst": "C", "path": ["A", "B", "C"], "rate": 4.0, "size": 10.0}),
    DomainEvent(timestamp=9, type="WorkloadStarted", payload={"workload_id": "W1", "server_id": "S1", "cpu_demand": 3.0, "memory_demand": 2.0, "size": 4.0, "cpu_usage_rate": 1.5}),
    DomainEvent(timestamp=10, type="WorkloadStarted", payload={"workload_id": "W2", "server_id": "S2", "cpu_demand": 2.0, "memory_demand": 2.0, "size": 3.0, "cpu_usage_rate": 1.0}),
    DomainEvent(timestamp=11, type="Tick", payload={"delta_time": 1.0}),
    DomainEvent(timestamp=12, type="Tick", payload={"delta_time": 1.5}),
]
for event in events:
    twin.ingest_event(event)

state = twin.state
from dataclasses import asdict
snapshot = twin.get_snapshot()
result = {
    "state": {
        "version_counter": state.version_counter,
        "event_counter": state.event_counter,
        "link_backlog": state.link_backlog,
        "cpu_usage": state.cpu_usage,
        "memory_usage": state.memory_usage,
        "active_workloads": sorted(state.active_workloads.keys()),
        "active_links": sorted(state.active_link_indices),
        "active_servers": sorted(state.active_server_indices),
    },
    "snapshot": asdict(snapshot),
    "event_log": [(e.timestamp, e.type, dict(e.payload), e.version, str(e.event_id)) for e in twin.event_log],
}
print(json.dumps(result, sort_keys=True))
'''


def _run_once(hash_seed: str) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    env["PYTHONHASHSEED"] = hash_seed
    proc = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(proc.stdout)


def test_tick_structural_determinism_across_fresh_interpreters() -> None:
    run_a = _run_once("11")
    run_b = _run_once("222")

    assert run_a["state"] == run_b["state"]
    assert run_a["snapshot"] == run_b["snapshot"]
    assert run_a["state"]["active_links"] == run_b["state"]["active_links"]
    assert run_a["state"]["active_servers"] == run_b["state"]["active_servers"]
    assert run_a["event_log"] == run_b["event_log"]
