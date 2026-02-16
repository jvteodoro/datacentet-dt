Perfeito. Vamos para o **A2 — Identifiable**, mantendo **exatamente o mesmo rigor** do Observable:
**Design by Contract (invariantes, pré-condições, pós-condições) + TDD primeiro**.

Vou seguir a mesma estrutura fixa.

---

# A2 — **Identifiable**

## 1️⃣ Definição conceitual (controle + epistemologia)

**Identifiable** é uma grandeza **não diretamente observável**, cujo valor é **inferido/identificado** a partir de:

* observáveis,
* histórico,
* modelos (físicos, estatísticos, ML),
* hipóteses explícitas.

> Um Identifiable **não é estado por si só** (a menos que você o promova conscientemente).
> Ele é uma **afirmação epistêmica inferida**, com suporte e limites claros.

Exemplos:

* eficiência de uma PSU,
* resistência equivalente,
* coeficiente térmico,
* fator de perdas.

---

## 2️⃣ Contrato Formal do Identifiable (Design by Contract)

### 🔒 Invariantes (sempre verdadeiros)

**I1 — Identidade semântica**

* `name` é string não vazia e estável

**I2 — Valor inferido explícito**

* `estimated_value` existe (não é `None`)

**I3 — Incerteza / confiança explícita**

* `uncertainty ≥ 0` **OU**
* `confidence ∈ (0, 1]`
* Pelo menos **um** dos dois deve existir

**I4 — Origem da inferência**

* `method` descreve o método de identificação
* `support` lista as fontes/observáveis usadas

**I5 — Contexto temporal**

* `timestamp` explícito (inteiro lógico)

**I6 — Epistemicidade correta**

* `epistemic_type == "inferred"`

**I7 — Imutabilidade**

* Após criação, o Identifiable não pode ser mutado silenciosamente

---

### ▶️ Pré-condições (antes de criar)

**P1**

* `name` é `str` não vazia

**P2**

* `estimated_value` não é `None`

**P3**

* `timestamp` é `int`

**P4**

* `method` é `str` não vazia

**P5**

* `support` é lista não vazia (referências semânticas)

**P6**

* Pelo menos um entre `uncertainty` ou `confidence` é fornecido e válido

---

### ⏹️ Pós-condições (após criação)

**Q1**

* O objeto expõe exatamente os valores fornecidos

**Q2**

* `to_dict()` contém metadados epistêmicos completos

**Q3**

* O objeto é imutável

---

## 3️⃣ Testes TDD — primeiro

### 📄 `tests/properties/identifiable/test_identifiable_properties.py`

```python
import pytest
from hypothesis import given, strategies as st

from domain.core.identifiable import (
    Identifiable,
    IdentifiableInvariantViolation,
)


# -------------------------
# Estratégias
# -------------------------

valid_names = st.text(min_size=1)
valid_methods = st.text(min_size=1)
valid_support = st.lists(st.text(min_size=1), min_size=1)
valid_values = st.floats(allow_nan=False, allow_infinity=False)
valid_uncertainty = st.floats(min_value=0, allow_nan=False, allow_infinity=False)
valid_confidence = st.floats(min_value=1e-6, max_value=1.0)
valid_timestamps = st.integers()


# -------------------------
# Invariantes estruturais
# -------------------------

@given(
    name=valid_names,
    value=valid_values,
    uncertainty=valid_uncertainty,
    timestamp=valid_timestamps,
    method=valid_methods,
    support=valid_support,
)
def test_I1_to_I6_identifiable_with_uncertainty_is_created(
    name, value, uncertainty, timestamp, method, support
):
    ident = Identifiable(
        name=name,
        estimated_value=value,
        uncertainty=uncertainty,
        timestamp=timestamp,
        method=method,
        support=support,
    )

    assert ident.name == name
    assert ident.estimated_value == value
    assert ident.uncertainty == uncertainty
    assert ident.timestamp == timestamp
    assert ident.method == method
    assert ident.support == support


@given(
    name=valid_names,
    value=valid_values,
    confidence=valid_confidence,
    timestamp=valid_timestamps,
    method=valid_methods,
    support=valid_support,
)
def test_I3_identifiable_with_confidence_is_created(
    name, value, confidence, timestamp, method, support
):
    ident = Identifiable(
        name=name,
        estimated_value=value,
        confidence=confidence,
        timestamp=timestamp,
        method=method,
        support=support,
    )

    assert ident.confidence == confidence
    assert ident.uncertainty is None


def test_I3_requires_uncertainty_or_confidence():
    with pytest.raises(IdentifiableInvariantViolation):
        Identifiable(
            name="efficiency",
            estimated_value=0.9,
            timestamp=0,
            method="least_squares",
            support=["voltage", "current"],
        )


def test_I7_identifiable_is_immutable():
    ident = Identifiable(
        name="resistance",
        estimated_value=10.0,
        uncertainty=0.5,
        timestamp=1,
        method="regression",
        support=["voltage", "current"],
    )

    with pytest.raises(IdentifiableInvariantViolation):
        ident._estimated_value = 12.0


def test_I6_epistemic_type_is_inferred():
    ident = Identifiable(
        name="loss_factor",
        estimated_value=0.1,
        uncertainty=0.02,
        timestamp=5,
        method="model_fit",
        support=["power_in", "power_out"],
    )

    data = ident.to_dict()
    assert data["epistemic_type"] == "inferred"
```

---

## 4️⃣ Implementação mínima (satisfazendo os testes)

### 📄 `domain/core/identifiable.py`

```python
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
```

---

## 5️⃣ Checklist atualizado

| ID | Objeto           | Status                               |
| -- | ---------------- | ------------------------------------ |
| A1 | Observable       | ✅ concluído                          |
| A2 | **Identifiable** | ✅ **concluído (baseline congelado)** |
| B1 | StateVariable    | ⬜ próximo                            |

---

## Próximo passo

O próximo objeto é **B1 — StateVariable**, onde entra **dinâmica, memória e tempo** (controle de verdade).

Se quiser manter o ritmo, diga:

> **“Vamos para o StateVariable”**

e seguimos com o mesmo rigor (DbC + TDD).
