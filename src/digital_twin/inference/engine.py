from __future__ import annotations

from enum import Enum
from types import MappingProxyType
from typing import Mapping

from digital_twin.domain.snapshot import TwinSnapshot

from .contracts import validate_parameter_vector
from .parameter import ParameterVector
from .registry import StrategyRegistry
from .store import ParameterStore


class InferenceMode(Enum):
    LIVE = "live"
    REPLAY = "replay"
    DISABLED = "disabled"


class InferenceEngine:
    def __init__(
        self,
        registry: StrategyRegistry,
        *,
        mode: InferenceMode = InferenceMode.LIVE,
        parameter_store: ParameterStore | None = None,
    ) -> None:
        self._registry = registry
        self._latest_parameters: dict[str, ParameterVector] = {}
        self._initialized = False
        self._mode = mode
        self._parameter_store = parameter_store

    def _validate_strategy_vector(self, strategy_id: str, parameter_vector: ParameterVector, previous_timestamp: int | None = None) -> None:
        if parameter_vector.strategy_id != strategy_id:
            raise ValueError("parameter strategy_id must match strategy name")
        validate_parameter_vector(parameter_vector, previous_timestamp=previous_timestamp)

    def _persist(self, parameter_vector: ParameterVector) -> None:
        if self._parameter_store is not None:
            self._parameter_store.append(parameter_vector)

    def _initialize_strategies(self, snapshot: TwinSnapshot) -> None:
        for strategy in self._registry.active_strategies():
            strategy.initialize(snapshot)
            parameter_vector = strategy.get_parameters()
            self._validate_strategy_vector(strategy.name(), parameter_vector)
            self._latest_parameters[strategy.name()] = parameter_vector
            self._persist(parameter_vector)
        self._initialized = True

    def on_snapshot(self, snapshot: TwinSnapshot) -> Mapping[str, ParameterVector]:
        if self._mode is InferenceMode.DISABLED:
            return MappingProxyType(dict(self._latest_parameters))

        if not self._initialized:
            self._initialize_strategies(snapshot)

        for strategy in self._registry.active_strategies():
            previous = self._latest_parameters.get(strategy.name())
            result = strategy.update(snapshot)
            self._validate_strategy_vector(
                strategy.name(),
                result.parameter_vector,
                previous_timestamp=previous.timestamp if previous is not None else None,
            )
            self._latest_parameters[strategy.name()] = result.parameter_vector
            self._persist(result.parameter_vector)

        return MappingProxyType(dict(self._latest_parameters))

    def get_parameters(self) -> Mapping[str, ParameterVector]:
        return MappingProxyType(dict(self._latest_parameters))
