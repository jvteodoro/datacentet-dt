import pytest

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.optimization.action import ActionProposal, deterministic_action_id
from digital_twin.optimization.contracts import validate_action_proposal


def _snapshot(version: int = 4) -> TwinSnapshot:
    return TwinSnapshot(
        version_counter=version,
        event_counter=version,
        total_nodes=0,
        total_links=0,
        total_servers=0,
        active_flows_count=0,
        total_active_workloads=0,
        total_backlog=0.0,
        total_active_links=0,
        total_active_servers=0,
        aggregate_cpu_usage=0.0,
        aggregate_memory_usage=0.0,
        link_backlog=(),
        cpu_usage=(),
        memory_usage=(),
        topology_node_ids=(),
        topology_adjacency=(),
        topology_link_capacity=(),
        topology_links=(),
        compute_server_ids=(),
        compute_cpu_capacity=(),
        compute_memory_capacity=(),
        active_flows=(),
        server_workload_count=(),
        active_workloads=(),
        active_link_indices=(),
        active_server_indices=(),
    )


def _valid_action(snapshot: TwinSnapshot) -> ActionProposal:
    payload = {"scale": 0.9}
    expected_effect = {"backlog_rate": -0.1}
    return ActionProposal(
        action_id=deterministic_action_id(
            strategy_id="baseline",
            kind="rate_limit",
            target="ingestion",
            payload=payload,
            expected_effect=expected_effect,
            timestamp=snapshot.version_counter,
        ),
        kind="rate_limit",
        target="ingestion",
        payload=payload,
        expected_effect=expected_effect,
        timestamp=snapshot.version_counter,
        strategy_id="baseline",
    )


def test_validate_action_proposal_accepts_valid_action() -> None:
    snapshot = _snapshot()
    validate_action_proposal(_valid_action(snapshot), snapshot, params={})


def test_validate_action_proposal_rejects_non_deterministic_id() -> None:
    snapshot = _snapshot()
    action = _valid_action(snapshot)
    bad = ActionProposal(
        action_id="bad-id",
        kind=action.kind,
        target=action.target,
        payload=action.payload,
        expected_effect=action.expected_effect,
        timestamp=action.timestamp,
        strategy_id=action.strategy_id,
    )
    with pytest.raises(ValueError, match="deterministic"):
        validate_action_proposal(bad, snapshot, params={})


def test_validate_action_proposal_rejects_nan_payload() -> None:
    snapshot = _snapshot()
    payload = {"scale": float("nan")}
    expected_effect = {"backlog_rate": -0.1}
    action = ActionProposal(
        action_id=deterministic_action_id(
            strategy_id="baseline",
            kind="rate_limit",
            target="ingestion",
            payload={"scale": 0.9},
            expected_effect=expected_effect,
            timestamp=snapshot.version_counter,
        ),
        kind="rate_limit",
        target="ingestion",
        payload=payload,
        expected_effect=expected_effect,
        timestamp=snapshot.version_counter,
        strategy_id="baseline",
    )
    with pytest.raises(ValueError, match="finite"):
        validate_action_proposal(action, snapshot, params={})
