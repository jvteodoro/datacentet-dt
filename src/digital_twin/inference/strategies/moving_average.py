from __future__ import annotations

from digital_twin.domain.snapshot import TwinSnapshot

from ..parameter import ParameterVector
from ..result import InferenceResult
from ..strategy import InferenceStrategy


class MovingAverageStrategy(InferenceStrategy):
    """Online O(1)-memory moving average over active-entity metrics."""

    def __init__(self, metrics: tuple[str, ...] = ("active_link_count", "cpu_usage_per_server", "backlog")) -> None:
        if not metrics:
            raise ValueError("metrics must not be empty")
        self._metrics = metrics
        self._running_count = 0
        self._current_means = {metric: 0.0 for metric in metrics}
        self._latest = ParameterVector(
            values=tuple(0.0 for _ in metrics),
            covariance=None,
            timestamp=0,
            strategy_id=self.name(),
        )

    def name(self) -> str:
        return "moving_average"

    def initialize(self, snapshot: TwinSnapshot) -> None:
        self._running_count = 0
        self._current_means = {metric: 0.0 for metric in self._metrics}
        self._latest = ParameterVector(
            values=tuple(0.0 for _ in self._metrics),
            covariance=None,
            timestamp=snapshot.version_counter,
            strategy_id=self.name(),
        )

    def update(self, snapshot: TwinSnapshot) -> InferenceResult:
        self._running_count += 1

        for metric in self._metrics:
            observation = self._observe_metric(snapshot, metric)
            current = self._current_means[metric]
            updated = current + (observation - current) / self._running_count
            self._current_means[metric] = updated

        values = tuple(self._current_means[metric] for metric in self._metrics)
        self._latest = ParameterVector(
            values=values,
            covariance=None,
            timestamp=snapshot.version_counter,
            strategy_id=self.name(),
        )
        return InferenceResult(parameter_vector=self._latest, metadata={"running_count": float(self._running_count)})

    def get_parameters(self) -> ParameterVector:
        return self._latest

    def _observe_metric(self, snapshot: TwinSnapshot, metric: str) -> float:
        if metric == "active_link_count":
            return float(snapshot.active_link_count)

        if metric == "cpu_usage_per_server":
            if snapshot.active_server_count == 0:
                return 0.0
            return snapshot.total_cpu_usage / float(snapshot.active_server_count)

        if metric == "backlog":
            if snapshot.active_link_count == 0:
                return 0.0
            return snapshot.total_backlog / float(snapshot.active_link_count)

        raise ValueError(f"unsupported moving-average metric: {metric}")
