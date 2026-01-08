"""
Identifiable — Domain Core Object (BASELINE v1.0)

Representa uma grandeza NÃO diretamente observável,
inferida a partir de observações e modelos.
"""

from typing import Any, Dict, List
from copy import deepcopy


class IdentifiableInvariantViolation(Exception):
    """
    Violação de invariante do Identifiable.
    """
    pass


class Identifiable:
    """
    Identifiable (Design by Contract).

    Invariantes:
    - identidade semântica
    - valor inferido explícito
    - incerteza ou confiança explícita
    - origem da inferência
    - contexto temporal
    - imutabilidade
    """

    def __init__(
        self,
        *,
        name: str,
        estimated_value: Any,
        timestamp: int,
        method: str,
        support: List[str],
        uncertainty: float | None = None,
        confidence: float | None = None,
    ):
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(name, str) or not name.strip():
            raise IdentifiableInvariantViolation("I1: invalid name")

        if estimated_value is None:
            raise IdentifiableInvariantViolation("I2: estimated_value must be explicit")

        if not isinstance(timestamp, int):
            raise IdentifiableInvariantViolation("I5: timestamp must be integer")

        if not isinstance(method, str) or not method.strip():
            raise IdentifiableInvariantViolation("I4: invalid method")

        if not isinstance(support, list) or not support:
            raise IdentifiableInvariantViolation("I4: support must be non-empty list")

        if uncertainty is None and confidence is None:
            raise IdentifiableInvariantViolation(
                "I3: uncertainty or confidence must be provided"
            )

        if uncertainty is not None:
            if not isinstance(uncertainty, (int, float)) or uncertainty < 0:
                raise IdentifiableInvariantViolation(
                    "I3: uncertainty must be >= 0"
                )

        if confidence is not None:
            if not isinstance(confidence, (int, float)) or not (0 < confidence <= 1):
                raise IdentifiableInvariantViolation(
                    "I3: confidence must be in (0, 1]"
                )

        # -------------------------
        # Estado interno (imutável)
        # -------------------------
        self._name = name
        self._estimated_value = estimated_value
        self._uncertainty = uncertainty
        self._confidence = confidence
        self._timestamp = timestamp
        self._method = method
        self._support = list(support)

        self._sealed = True

    # -------------------------
    # Acesso somente leitura
    # -------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def estimated_value(self) -> Any:
        return self._estimated_value

    @property
    def uncertainty(self) -> float | None:
        return self._uncertainty

    @property
    def confidence(self) -> float | None:
        return self._confidence

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def method(self) -> str:
        return self._method

    @property
    def support(self) -> List[str]:
        return list(self._support)

    # -------------------------
    # Imutabilidade
    # -------------------------

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise IdentifiableInvariantViolation(
                "I7: identifiable is immutable after creation"
            )
        super().__setattr__(key, value)

    # -------------------------
    # Interface canônica
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Representação epistêmica neutra para snapshot.
        """
        return {
            "name": self.name,
            "estimated_value": deepcopy(self.estimated_value),
            "uncertainty": self.uncertainty,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "method": self.method,
            "support": list(self.support),
            "epistemic_type": "inferred",
        }
