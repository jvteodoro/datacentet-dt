from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from .parameter import ParameterVector


class ParameterStore(ABC):
    """Persistence port for immutable inferred parameters."""

    @abstractmethod
    def append(self, parameter_vector: ParameterVector) -> None:
        """Persist one validated immutable parameter vector."""

    @abstractmethod
    def load_all(self) -> Iterable[ParameterVector]:
        """Return all persisted parameter vectors in append order."""
