from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping
from uuid import NAMESPACE_URL, uuid5

JsonPrimitive = float | int | str


@dataclass(frozen=True, slots=True)
class ActionProposal:
    action_id: str
    kind: str
    target: str
    payload: Mapping[str, JsonPrimitive]
    expected_effect: Mapping[str, float]
    timestamp: int
    strategy_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
        object.__setattr__(self, "expected_effect", MappingProxyType(dict(self.expected_effect)))


@dataclass(frozen=True, slots=True)
class OptimizationResult:
    actions: tuple[ActionProposal, ...]
    metadata: Mapping[str, str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def deterministic_action_id(
    *,
    strategy_id: str,
    kind: str,
    target: str,
    payload: Mapping[str, JsonPrimitive],
    expected_effect: Mapping[str, float],
    timestamp: int,
) -> str:
    payload_token = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), allow_nan=False)
    effect_token = json.dumps(dict(expected_effect), sort_keys=True, separators=(",", ":"), allow_nan=False)
    canonical = f"{strategy_id}|{kind}|{target}|{timestamp}|{payload_token}|{effect_token}"
    return str(uuid5(NAMESPACE_URL, canonical))
