"""
StateVariable — Domain Core Object (BASELINE v1.0)

Representa uma variável de estado do sistema,
portadora de memória e dinâmica implícita.
"""

from typing import Any, Dict
from copy import deepcopy


class StateVariableInvariantViolation(Exception):
    """
    Violação de invariante da StateVariable.
    """
    pass


class StateVariable:
    """
    StateVariable (Design by Contract).

    Invariantes:
    - identidade semântica
    - valor explícito
    - incerteza explícita
    - contexto temporal
    - imutabilidade
    """

    def __init__(
        self,
        *,
        name: str,
        value: Any,
        uncertainty: float,
        timestamp: int,
    ):
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(name, str) or not name.strip():
            raise StateVariableInvariantViolation("SV1: invalid name")

        if value is None:
            raise StateVariableInvariantViolation("SV2: value must be explicit")

        if not isinstance(uncertainty, (int, float)) or uncertainty < 0:
            raise StateVariableInvariantViolation(
                "SV3: uncertainty must be >= 0"
            )

        if not isinstance(timestamp, int):
            raise StateVariableInvariantViolation("SV4: timestamp must be integer")

        # -------------------------
        # Estado interno (imutável)
        # -------------------------
        self._name = name
        self._value = value
        self._uncertainty = uncertainty
        self._timestamp = timestamp

        self._sealed = True

    # -------------------------
    # Acesso somente leitura
    # -------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Any:
        return self._value

    @property
    def uncertainty(self) -> float:
        return self._uncertainty

    @property
    def timestamp(self) -> int:
        return self._timestamp

    # -------------------------
    # Imutabilidade
    # -------------------------

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise StateVariableInvariantViolation(
                "SV7: state variable is immutable after creation"
            )
        super().__setattr__(key, value)

    # -------------------------
    # Interface canônica
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Representação neutra do estado para snapshot.
        """
        return {
            "name": self.name,
            "value": deepcopy(self.value),
            "uncertainty": self.uncertainty,
            "timestamp": self.timestamp,
            "epistemic_type": "state",
        }
