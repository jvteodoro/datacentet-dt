"""
StateVector — Domain Core Object (BASELINE v1.0)

Representa o vetor de estado do sistema em um instante lógico.
"""

import numpy as np
from typing import List, Dict, Any

from domain.core.state_variable import StateVariable
from domain.core.covariance_utils import (
    CovarianceDomainViolation,
    symmetrize_covariance,
    validate_psd_covariance,
)


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

        dim = len(variables)
        normalized_covariance = symmetrize_covariance(covariance)
        try:
            validate_psd_covariance(
                normalized_covariance,
                expected_dim=dim,
                context="SVEC4 covariance",
            )
        except CovarianceDomainViolation as exc:
            raise StateVectorInvariantViolation(
                f"SVEC4: invalid covariance matrix: {exc}"
            ) from exc

        # -------------------------
        # Estado interno (imutável)
        # -------------------------
        self._variables = list(variables)
        self._covariance = normalized_covariance.copy()
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
