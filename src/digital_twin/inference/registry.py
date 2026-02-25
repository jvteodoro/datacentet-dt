from __future__ import annotations

from .strategy import InferenceStrategy


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, InferenceStrategy] = {}

    def register(self, strategy: InferenceStrategy) -> None:
        strategy_id = strategy.name()
        if strategy_id in self._strategies:
            raise ValueError(f"strategy already registered: {strategy_id}")
        self._strategies[strategy_id] = strategy

    def active_strategies(self) -> tuple[InferenceStrategy, ...]:
        return tuple(self._strategies[key] for key in sorted(self._strategies))
