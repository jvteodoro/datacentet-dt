"""
StateVector — Domain Core Object (BASELINE v1.0)

Representa o vetor de estado do sistema em um instante lógico.
"""

import numpy as np
from typing import List, Dict, Any
from copy import deepcopy

from src.domain.core.state_variable import StateVariable


class StateVectorInvariantViolation(Exception):
    """
    Violação de invariante do StateVector.
    """
    pass


class StateVector:
    """
    StateVector (Design by Contract).

    Agrega múltiplas StateVariable em um estado composto,
    com incerteza conjunta explícita.
    """

    def __init__(
        self,
        *,
        variables: List[StateVariable],
        covariance: np.ndarray,
    ):
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(variables, list) or not variables:
            raise StateVectorInvariantViolation(
                "SVEC1: variables must be a non-empty list"
            )

        if not all(isinstance(v, StateVariable) for v in variables):
            raise StateVectorInvariantViolation(
                "SVEC1: all elements must be StateVariable"
            )

        names = [v.name for v in variables]
        if len(names) != len(set(names)):
            raise StateVectorInvariantViolation(
                "SVEC2: variable names must be unique"
            )

        timestamps = {v.timestamp for v in variables}
        if len(timestamps) != 1:
            raise StateVectorInvariantViolation(
                "SVEC3: all variables must share the same timestamp"
            )

        if not isinstance(covariance, np.ndarray):
            raise StateVectorInvariantViolation(
                "SVEC4: covariance must be numpy array"
            )

        dim = len(variables)
        if covariance.shape != (dim, dim):
            raise StateVectorInvariantViolation(
                "SVEC4: covariance dimension mismatch"
            )

        if not np.allclose(covariance, covariance.T):
            raise StateVectorInvariantViolation(
                "SVEC4: covariance must be symmetric"
            )

        eigvals = np.linalg.eigvals(covariance)
        if (eigvals < -1e-8).any():
            raise StateVectorInvariantViolation(
                "SVEC4: covariance must be positive semidefinite"
            )

        # -------------------------
        # Estado interno (imutável)
        # -------------------------
        self._variables = list(variables)
        self._covariance = covariance.copy()
        self._timestamp = variables[0].timestamp

        self._sealed = True

    # -------------------------
    # Acesso somente leitura
    # -------------------------

    @property
    def variables(self) -> List[StateVariable]:
        return list(self._variables)

    @property
    def covariance(self) -> np.ndarray:
        return self._covariance.copy()

    @property
    def timestamp(self) -> int:
        return self._timestamp

    # -------------------------
    # Imutabilidade
    # -------------------------

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise StateVectorInvariantViolation(
                "SVEC6: state vector is immutable after creation"
            )
        super().__setattr__(key, value)

    # -------------------------
    # Interface canônica
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Representação autocontida do vetor de estado para snapshot.
        """
        return {
            "variables": [v.to_dict() for v in self.variables],
            "covariance": self.covariance,
            "timestamp": self.timestamp,
            "epistemic_type": "state_vector",
        }
