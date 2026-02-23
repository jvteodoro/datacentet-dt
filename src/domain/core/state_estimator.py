"""
StateEstimator — Domain Core Object (BASELINE v1.0)

Responsável por PROPOR um novo StateVector
a partir de observações e estado anterior.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.core.state_vector import StateVector
from domain.core.observable import Observable
from domain.core.observation_model import ObservationModel
from domain.contracts.temporal import TemporalContract, TemporalViolation


class StateEstimatorInvariantViolation(Exception):
    """
    Violação de invariante do StateEstimator.
    """
    pass


class StateEstimator(ABC):
    """
    StateEstimator (Design by Contract).

    Produz hipóteses de estado.
    Nunca valida contratos globais.
    """

    def estimate(
        self,
        *,
        observables: List[Observable],
        observation_model: ObservationModel,
        previous_state: Optional[StateVector],
    ) -> StateVector:
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(observables, list) or not observables:
            raise StateEstimatorInvariantViolation(
                "SE: observables must be a non-empty list"
            )

        if not all(isinstance(o, Observable) for o in observables):
            raise StateEstimatorInvariantViolation(
                "SE: all observables must be Observable"
            )

        if not isinstance(observation_model, ObservationModel):
            raise StateEstimatorInvariantViolation(
                "SE: invalid observation_model"
            )

        if previous_state is not None and not isinstance(previous_state, StateVector):
            raise StateEstimatorInvariantViolation(
                "SE: previous_state must be StateVector or None"
            )

        # -------------------------
        # Estimação concreta
        # -------------------------
        new_state = self._estimate(
            observables=observables,
            previous_state=previous_state,
            model=observation_model,
        )

        # -------------------------
        # Pós-condições
        # -------------------------
        if not isinstance(new_state, StateVector):
            raise StateEstimatorInvariantViolation(
                "SE2: estimator must return StateVector"
            )

        if previous_state is not None:
            try:
                TemporalContract.ensure_non_regressive(
                    previous=previous_state.timestamp,
                    current=new_state.timestamp,
                    code="SE3",
                )
            except TemporalViolation as exc:
                raise StateEstimatorInvariantViolation(str(exc)) from exc

        return new_state

    # -------------------------------------------------
    # Implementação concreta
    # -------------------------------------------------

    @abstractmethod
    def _estimate(
        self,
        *,
        observables: List[Observable],
        previous_state: Optional[StateVector],
        model: ObservationModel,
    ) -> StateVector:
        """
        Implementação concreta do algoritmo de estimação.
        """
        raise NotImplementedError
