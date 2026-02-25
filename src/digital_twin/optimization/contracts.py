from __future__ import annotations

import math
from typing import Any

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.parameter import ParameterVector

from .action import ActionProposal, JsonPrimitive, deterministic_action_id

ALLOWED_ACTION_KINDS = frozenset({"scheduling", "routing", "rate_limit"})


def validate_action_proposal(
    action: ActionProposal,
    snapshot: TwinSnapshot,
    params: dict[str, ParameterVector],
) -> None:
    del params

    if action.timestamp != snapshot.version_counter:
        raise ValueError("action timestamp must match snapshot version_counter")

    if not action.action_id:
        raise ValueError("action_id must be non-empty")

    if action.kind not in ALLOWED_ACTION_KINDS:
        raise ValueError(f"unsupported action kind: {action.kind}")

    for key, value in action.payload.items():
        _validate_json_primitive(key, value)

    for metric, value in action.expected_effect.items():
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"expected_effect contains non-finite numeric value: {metric}")

    expected_id = deterministic_action_id(
        strategy_id=action.strategy_id,
        kind=action.kind,
        target=action.target,
        payload=action.payload,
        expected_effect=action.expected_effect,
        timestamp=action.timestamp,
    )
    if action.action_id != expected_id:
        raise ValueError("action_id must be deterministic")


def _validate_json_primitive(key: str, value: Any) -> None:
    if isinstance(value, bool):
        raise ValueError(f"payload value for '{key}' must be float|int|str")

    if not isinstance(value, (float, int, str)):
        raise ValueError(f"payload value for '{key}' must be float|int|str")

    if isinstance(value, (float, int)) and (math.isnan(value) or math.isinf(value)):
        raise ValueError(f"payload numeric value for '{key}' must be finite")


__all__ = ["ALLOWED_ACTION_KINDS", "JsonPrimitive", "validate_action_proposal"]
