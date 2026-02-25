from __future__ import annotations

from enum import Enum
from types import MappingProxyType
from typing import Mapping

from digital_twin.domain.event import DomainEvent, EVENT_CONTROL_ACTION_PROPOSED
from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.parameter import ParameterVector

from .action import ActionProposal, OptimizationResult
from .contracts import validate_action_proposal
from .registry import StrategyRegistry


class OptimizationMode(Enum):
    LIVE = "live"
    REPLAY = "replay"
    DISABLED = "disabled"


class OptimizationEngine:
    def __init__(self, registry: StrategyRegistry, *, mode: OptimizationMode = OptimizationMode.LIVE) -> None:
        self._registry = registry
        self._mode = mode
        self._initialized = False
        self._latest_actions: tuple[ActionProposal, ...] = ()

    def _initialize(self, snapshot: TwinSnapshot, params: dict[str, ParameterVector]) -> None:
        for strategy in self._registry.active_strategies():
            strategy.initialize(snapshot, params)
        self._initialized = True

    def on_snapshot(self, snapshot: TwinSnapshot, params: Mapping[str, ParameterVector]) -> OptimizationResult:
        if self._mode is OptimizationMode.DISABLED:
            self._latest_actions = ()
            return OptimizationResult(actions=(), metadata={"mode": self._mode.value})

        mutable_params = dict(params)
        if not self._initialized:
            self._initialize(snapshot, mutable_params)

        actions: list[ActionProposal] = []
        for strategy in self._registry.active_strategies():
            proposed = strategy.propose(snapshot, mutable_params)
            actions.extend(proposed)

        finalized_actions = tuple(actions)
        for action in finalized_actions:
            validate_action_proposal(action, snapshot, mutable_params)

        self._latest_actions = finalized_actions
        return OptimizationResult(actions=finalized_actions, metadata={"mode": self._mode.value})

    def latest_actions(self) -> tuple[ActionProposal, ...]:
        return self._latest_actions

    def as_domain_events(self) -> tuple[DomainEvent, ...]:
        return tuple(_to_control_event(action) for action in self._latest_actions)

    def get_latest_actions(self) -> tuple[ActionProposal, ...]:
        return self._latest_actions


def _to_control_event(action: ActionProposal) -> DomainEvent:
    return DomainEvent(
        timestamp=action.timestamp,
        type=EVENT_CONTROL_ACTION_PROPOSED,
        payload=MappingProxyType(
            {
                "action_id": action.action_id,
                "kind": action.kind,
                "target": action.target,
                "payload": dict(action.payload),
                "expected_effect": dict(action.expected_effect),
                "strategy_id": action.strategy_id,
            }
        ),
    )
