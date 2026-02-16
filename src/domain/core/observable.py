"""
Observable — Domain Core Object (BASELINE v1.0)

Representa uma grandeza diretamente observável do mundo.
"""

from typing import Any, Dict
from copy import deepcopy


class ObservableInvariantViolation(Exception):
    """
    Violação de invariante do Observable.
    """
    pass


class Observable:
    """
    Observable (Design by Contract).

    Invariantes:
    - identidade semântica
    - incerteza explícita
    - contexto temporal
    - imutabilidade
    - neutralidade epistêmica
    """

    def __init__(
        self,
        *,
        name: str,
        value: Any,
        uncertainty: float,
        confidence: float,
        timestamp: int,
        source: str,
    ):
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(name, str) or not name.strip():
            raise ObservableInvariantViolation("O1: invalid name")

        if value is None:
            raise ObservableInvariantViolation("O2: value must be explicit")

        if not isinstance(uncertainty, (int, float)) or uncertainty < 0:
            raise ObservableInvariantViolation("O3: uncertainty must be >= 0")
        

        if not isinstance(timestamp, int):
            raise ObservableInvariantViolation("O4: timestamp must be integer")

        if not isinstance(source, str) or not source.strip():
            raise ObservableInvariantViolation("O5: invalid source")
        
        if not isinstance(confidence, (int, float)) or confidence < 0:
            raise ObservableInvariantViolation("O6: confidence must be a >= 0 number")

        # -------------------------
        # Estado interno (imutável)
        # -------------------------
        self._name = name
        self._value = value
        self._uncertainty = uncertainty
        self._confidence = confidence
        self._timestamp = timestamp
        self._source = source

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

    @property
    def source(self) -> str:
        return self._source

    @property
    def confidence(self) -> int | float:
        return self._confidence
    
    # -------------------------
    # Imutabilidade
    # -------------------------

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise ObservableInvariantViolation(
                "O6: observable is immutable after creation"
            )
        super().__setattr__(key, value)

    # -------------------------
    # Interface canônica
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Representação neutra para snapshot.
        """
        return {
            "name": self.name,
            "value": deepcopy(self.value),
            "uncertainty": self.uncertainty,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "source": self.source,
            "epistemic_type": "observed",
        }
