from __future__ import annotations

from abc import ABC, abstractmethod

from digital_twin.domain.snapshot import TwinSnapshot

from .parameter import ParameterVector
from .result import InferenceResult


class InferenceStrategy(ABC):
    """Contract for online deterministic epistemic estimators.

    Requirements:
    - Online update only: update from current snapshot + local estimator state.
    - Deterministic evolution: same snapshot stream -> same parameters.
    - No domain mutation: strategies are read-only consumers of TwinSnapshot.
    """

    @abstractmethod
    def initialize(self, snapshot: TwinSnapshot) -> None:
        """Initialize internal estimator state from a snapshot."""

    @abstractmethod
    def update(self, snapshot: TwinSnapshot) -> InferenceResult:
        """Consume the next snapshot and return the latest inferred parameters."""

    @abstractmethod
    def get_parameters(self) -> ParameterVector:
        """Return latest immutable inferred parameters."""

    @abstractmethod
    def name(self) -> str:
        """Return stable strategy identifier."""
