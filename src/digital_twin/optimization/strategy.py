from __future__ import annotations

from abc import ABC, abstractmethod

from digital_twin.domain.snapshot import TwinSnapshot
from digital_twin.inference.parameter import ParameterVector

from .action import ActionProposal


class OptimizationStrategy(ABC):
    @abstractmethod
    def name(self) -> str:
        """Stable strategy identifier."""

    @abstractmethod
    def initialize(self, snapshot: TwinSnapshot, params: dict[str, ParameterVector]) -> None:
        """Initialize strategy-local state from immutable inputs."""

    @abstractmethod
    def propose(self, snapshot: TwinSnapshot, params: dict[str, ParameterVector]) -> tuple[ActionProposal, ...]:
        """Return deterministic action proposals for the given snapshot and parameters."""

    @abstractmethod
    def capabilities(self) -> dict[str, str]:
        """Metadata about supported optimization capabilities."""
