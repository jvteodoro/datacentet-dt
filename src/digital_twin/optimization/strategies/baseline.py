from __future__ import annotations

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.parameter import ParameterVector

from ..action import ActionProposal, deterministic_action_id
from ..strategy import OptimizationStrategy


class BaselineOptimizationStrategy(OptimizationStrategy):
    """Simple O(1) optimization scaffold using aggregated backlog metric only."""

    def __init__(self, backlog_threshold: float = 100.0, scale: float = 0.9) -> None:
        self._backlog_threshold = backlog_threshold
        self._scale = scale

    def name(self) -> str:
        return "baseline"

    def initialize(self, snapshot: TwinSnapshot, params: dict[str, ParameterVector]) -> None:
        del snapshot, params

    def capabilities(self) -> dict[str, str]:
        return {
            "kind": "rate_limit",
            "complexity": "O(1)",
            "scope": "aggregated_active_metrics",
            "target": "ingestion",
        }

    def propose(self, snapshot: TwinSnapshot, params: dict[str, ParameterVector]) -> tuple[ActionProposal, ...]:
        del params

        if snapshot.total_backlog <= self._backlog_threshold:
            return ()

        payload = {"scale": self._scale}
        expected_effect = {"backlog_rate": -0.1}
        action_id = deterministic_action_id(
            strategy_id=self.name(),
            kind="rate_limit",
            target="ingestion",
            payload=payload,
            expected_effect=expected_effect,
            timestamp=snapshot.version_counter,
        )
        return (
            ActionProposal(
                action_id=action_id,
                kind="rate_limit",
                target="ingestion",
                payload=payload,
                expected_effect=expected_effect,
                timestamp=snapshot.version_counter,
                strategy_id=self.name(),
            ),
        )
