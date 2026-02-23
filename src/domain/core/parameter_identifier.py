"""
ParameterIdentifier — Domain Core Object (BASELINE v1.0)

Responsável por PROPOR parâmetros identificáveis (Identifiables)
a partir de dados e/ou estado.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.core.observable import Observable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable
from domain.contracts.temporal import TemporalContract


class ParameterIdentifierInvariantViolation(Exception):
    """
    Violação de invariante do ParameterIdentifier.
    """
    pass


class ParameterIdentifier(ABC):
    """
    ParameterIdentifier (Design by Contract).

    Produz hipóteses de parâmetros do modelo.
    Nunca produz estado.
    """

    def identify(
        self,
        *,
        observables: List[Observable],
        state_vector: Optional[StateVector],
    ) -> List[Identifiable]:
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(observables, list):
            raise ParameterIdentifierInvariantViolation(
                "PI: observables must be a list"
            )

        if state_vector is not None and not isinstance(state_vector, StateVector):
            raise ParameterIdentifierInvariantViolation(
                "PI: state_vector must be StateVector or None"
            )

        if not observables and state_vector is None:
            raise ParameterIdentifierInvariantViolation(
                "PI: at least one data source required"
            )

        # -------------------------
        # Identificação concreta
        # -------------------------
        params = self._identify(
            observables=observables,
            state_vector=state_vector,
        )

        # -------------------------
        # Pós-condições / invariantes
        # -------------------------
        self._validate_output(params, observables, state_vector)

        return params

    # -------------------------------------------------
    # Validação local
    # -------------------------------------------------

    def _validate_output(
        self,
        params,
        observables,
        state_vector,
    ):
        if not isinstance(params, list) or not params:
            raise ParameterIdentifierInvariantViolation(
                "PI2: must return non-empty list of Identifiable"
            )

        for p in params:
            if not isinstance(p, Identifiable):
                raise ParameterIdentifierInvariantViolation(
                    "PI1: identifier cannot return non-Identifiable objects"
                )

            if p.timestamp is None:
                raise ParameterIdentifierInvariantViolation(
                    "PI3: identifiable must have timestamp"
                )

            if observables:
                max_ts = max(o.timestamp for o in observables)
                if TemporalContract.is_future(current=max_ts, candidate=p.timestamp):
                    raise ParameterIdentifierInvariantViolation(
                        "PI3: future data is not causally admissible (observables)"
                    )

            if state_vector:
                if TemporalContract.is_future(current=state_vector.timestamp, candidate=p.timestamp):
                    raise ParameterIdentifierInvariantViolation(
                        "PI3: future data is not causally admissible (state)"
                    )

    # -------------------------------------------------
    # Implementação concreta
    # -------------------------------------------------

    @abstractmethod
    def _identify(
        self,
        *,
        observables: List[Observable],
        state_vector: Optional[StateVector],
    ) -> List[Identifiable]:
        """
        Implementação concreta do algoritmo de identificação.
        """
        raise NotImplementedError