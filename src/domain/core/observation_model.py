"""
ObservationModel — Domain Core Object (BASELINE v1.0)

Define a ponte formal entre:
StateVector + Identifiables → Observáveis esperados
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable


class ObservationModelInvariantViolation(Exception):
    """
    Violação de invariante do ObservationModel.
    """
    pass


class PredictedObservable:
    """
    Representa um observável esperado (predito pelo modelo).
    """

    def __init__(self, *, name: str, predicted_value, timestamp: int):
        if not isinstance(name, str) or not name.strip():
            raise ObservationModelInvariantViolation("OM: invalid observable name")

        if predicted_value is None:
            raise ObservationModelInvariantViolation(
                "OM: predicted value must be explicit"
            )

        if not isinstance(timestamp, int):
            raise ObservationModelInvariantViolation(
                "OM: timestamp must be integer"
            )

        self._name = name
        self._predicted_value = predicted_value
        self._timestamp = timestamp

        self._sealed = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def predicted_value(self):
        return self._predicted_value

    @property
    def timestamp(self) -> int:
        return self._timestamp

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise ObservationModelInvariantViolation(
                "PredictedObservable is immutable"
            )
        super().__setattr__(key, value)


class ObservationModel(ABC):
    """
    ObservationModel (Design by Contract).

    Responsável por:
    - prever observáveis esperados
    - definir como calcular resíduos

    NÃO:
    - mede
    - valida
    - estima
    """

    # -------------------------------------------------
    # Interface obrigatória
    # -------------------------------------------------

    @abstractmethod
    def predicted_observables(self) -> List[str]:
        """
        Retorna os nomes dos observáveis que este modelo prediz.
        """
        raise NotImplementedError

    @abstractmethod
    def _predict(
        self,
        state_vector: StateVector,
        parameters: List[Identifiable],
    ) -> Dict[str, float]:
        """
        Implementação concreta do modelo:
        retorna {observable_name: predicted_value}
        """
        raise NotImplementedError

    # -------------------------------------------------
    # API pública (contratada)
    # -------------------------------------------------

    def predict(
        self,
        *,
        state_vector: StateVector,
        parameters: List[Identifiable],
    ) -> Dict[str, PredictedObservable]:
        # Pré-condições
        if not isinstance(state_vector, StateVector):
            raise ObservationModelInvariantViolation(
                "OM: invalid state_vector"
            )

        if not isinstance(parameters, list):
            raise ObservationModelInvariantViolation(
                "OM: parameters must be a list"
            )

        # Predição
        raw = self._predict(state_vector, parameters)

        # Pós-condições
        declared = set(self.predicted_observables())
        if set(raw.keys()) != declared:
            raise ObservationModelInvariantViolation(
                "OM2: predicted observables mismatch declaration"
            )

        timestamp = state_vector.timestamp

        return {
            name: PredictedObservable(
                name=name,
                predicted_value=value,
                timestamp=timestamp,
            )
            for name, value in raw.items()
        }

    # -------------------------------------------------
    # Residual (estático e puro)
    # -------------------------------------------------

    @staticmethod
    def residual(*, predicted: PredictedObservable, observed_value: float) -> float:
        """
        Residual (innovation) defined as:

            r = y_observed - y_predicted

        This sign convention is consistent with control theory
        and state estimation (e.g., Kalman filtering).
        """
        return observed_value - predicted.predicted_value

