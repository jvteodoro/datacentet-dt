"""
ObservableRegistry — Domain Internal Component (BASELINE v1.0)

Gerencia observações ao longo do tempo.
"""

from typing import List, Optional

from domain.core.observable import Observable
from domain.contracts.temporal import TemporalContract


class ObservableRegistryViolation(Exception):
    """
    Violação de contrato do ObservableRegistry.
    """
    pass


class ObservableRegistry:
    """
    Registry operacional de observáveis.

    NÃO:
    - infere
    - valida ciência
    - persiste
    """

    def __init__(self):
        self._observables: List[Observable] = []

    # -------------------------------------------------
    # Registro
    # -------------------------------------------------

    def register(self, observable: Observable) -> None:
        if not isinstance(observable, Observable):
            raise ObservableRegistryViolation(
                "OR1: only Observable instances can be registered"
            )

        # Não muta observável, apenas armazena
        self._observables.append(observable)

        # Mantém ordenação temporal estável para consultas determinísticas
        self._observables.sort(key=lambda o: o.timestamp)
    # -------------------------------------------------
    # Consultas
    # -------------------------------------------------

    def get_at(self, timestamp: int) -> List[Observable]:
        if not isinstance(timestamp, int):
            raise ObservableRegistryViolation(
                "OR2: timestamp must be integer"
            )

        return [
            o for o in self._observables
            if o.timestamp == timestamp
        ]

    def get_since(self, timestamp: int) -> List[Observable]:
        if not isinstance(timestamp, int):
            raise ObservableRegistryViolation(
                "OR2: timestamp must be integer"
            )

        return [
            o for o in self._observables
            if not TemporalContract.is_future(current=o.timestamp, candidate=timestamp)
        ]

    def latest_timestamp(self) -> Optional[int]:
        if not self._observables:
            return None
        return max(o.timestamp for o in self._observables)
