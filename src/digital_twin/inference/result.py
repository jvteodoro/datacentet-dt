from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .parameter import ParameterVector


@dataclass(frozen=True, slots=True)
class InferenceResult:
    parameter_vector: ParameterVector
    metadata: Mapping[str, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
