from __future__ import annotations

from typing import Mapping

from digital_twin.domain.event import DomainEvent
from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.domain.twin import DataCenterTwin
from digital_twin.inference.engine import InferenceEngine
from digital_twin.inference.parameter import ParameterVector
from digital_twin.inference.registry import StrategyRegistry
from digital_twin.inference.strategies.moving_average import MovingAverageStrategy


class InferenceEnabledTwin:
    """Application-layer composition of deterministic twin + inference engine."""

    def __init__(self, twin: DataCenterTwin | None = None) -> None:
        self._twin = twin if twin is not None else DataCenterTwin()
        registry = StrategyRegistry()
        registry.register(MovingAverageStrategy())
        self._inference_engine = InferenceEngine(registry)

    def ingest_event(self, event: DomainEvent) -> None:
        self._twin.ingest_event(event)
        self._inference_engine.on_snapshot(self._twin.get_snapshot())

    def get_snapshot(self) -> TwinSnapshot:
        return self._twin.get_snapshot()

    def get_parameters(self) -> Mapping[str, ParameterVector]:
        return self._inference_engine.get_parameters()
