Perfeito. Vamos começar **formalmente** pelo **A1 — Observable**, seguindo **Design by Contract (DbC)**, com **invariantes, pré-condições e pós-condições**, e **TDD primeiro**.

Vou estruturar assim (ordem fixa):

1️⃣ Definição conceitual
2️⃣ Contrato formal (Invariantes, Pré, Pós)
3️⃣ Testes TDD (property-based quando fizer sentido)
4️⃣ Implementação mínima que satisfaz os testes
5️⃣ Checklist atualizado

---

# A1 — **Observable**

## 1️⃣ Definição conceitual (controle + epistemologia)

**Observable** é uma grandeza **diretamente mensurável** do mundo.

> Um Observable **não é estado**, **não é inferência** e **não carrega dinâmica própria**.
> Ele é um **registro epistêmico de medição** em um instante lógico.

Exemplos:

* tensão, corrente, temperatura, vazão, potência instantânea

---

## 2️⃣ Contrato Formal do Observable (Design by Contract)

### 🔒 Invariantes (sempre verdadeiros)

**O1 — Identidade semântica**

* `name` é string não vazia e estável

**O2 — Valor explícito**

* `value` existe (não é `None`)

**O3 — Incerteza explícita**

* toda observação tem incerteza associada
* `uncertainty ≥ 0`

**O4 — Contexto temporal**

* toda observação tem `timestamp` explícito (inteiro lógico)

**O5 — Origem explícita**

* `source` identifica sensor/origem de medição

**O6 — Imutabilidade**

* após criação, nenhum campo pode ser mutado silenciosamente

**O7 — Neutralidade epistêmica**

* Observable **não declara verdade, confiança ou inferência**
* ele é sempre “observed”

---

### ▶️ Pré-condições (antes de criar)

**P1**

* `name` deve ser `str` não vazia

**P2**

* `timestamp` deve ser `int`

**P3**

* `uncertainty` deve ser número real `≥ 0`

**P4**

* `source` deve ser `str` não vazia

---

### ⏹️ Pós-condições (após criação)

**Q1**

* `observable.value == value` passado

**Q2**

* `observable.timestamp == timestamp`

**Q3**

* `observable` é imutável

**Q4**

* `observable.to_dict()` contém todos os campos contratuais

---

## 3️⃣ Testes TDD — primeiro

### 📄 `tests/properties/observable/test_observable_properties.py`

```python
import pytest
from hypothesis import given, strategies as st

from domain.core.observable import Observable, ObservableInvariantViolation


# -------------------------
# Estratégias
# -------------------------

valid_names = st.text(min_size=1)
valid_sources = st.text(min_size=1)
valid_values = st.floats(allow_nan=False, allow_infinity=False)
valid_uncertainty = st.floats(min_value=0, allow_nan=False, allow_infinity=False)
valid_timestamps = st.integers()


# -------------------------
# Invariantes estruturais
# -------------------------

@given(
    name=valid_names,
    value=valid_values,
    uncertainty=valid_uncertainty,
    timestamp=valid_timestamps,
    source=valid_sources,
)
def test_O1_to_O5_valid_observable_is_created(
    name, value, uncertainty, timestamp, source
):
    obs = Observable(
        name=name,
        value=value,
        uncertainty=uncertainty,
        timestamp=timestamp,
        source=source,
    )

    assert obs.name == name
    assert obs.value == value
    assert obs.uncertainty == uncertainty
    assert obs.timestamp == timestamp
    assert obs.source == source


def test_O3_uncertainty_must_be_non_negative():
    with pytest.raises(ObservableInvariantViolation):
        Observable(
            name="voltage",
            value=220.0,
            uncertainty=-1.0,
            timestamp=0,
            source="sensor",
        )


def test_O6_observable_is_immutable():
    obs = Observable(
        name="temperature",
        value=25.0,
        uncertainty=0.5,
        timestamp=10,
        source="sensor",
    )

    with pytest.raises(ObservableInvariantViolation):
        obs._value = 30.0


def test_O7_observable_is_epistemically_neutral():
    obs = Observable(
        name="current",
        value=10.0,
        uncertainty=0.2,
        timestamp=5,
        source="sensor",
    )

    data = obs.to_dict()
    assert data["epistemic_type"] == "observed"
```

---

## 4️⃣ Implementação mínima (satisfazendo os testes)

### 📄 `domain/core/observable.py`

```python
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

        # -------------------------
        # Estado interno (imutável)
        # -------------------------
        self._name = name
        self._value = value
        self._uncertainty = uncertainty
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
            "timestamp": self.timestamp,
            "source": self.source,
            "epistemic_type": "observed",
        }
```

---

## 5️⃣ Checklist atualizado

| ID | Objeto         | Status                               |
| -- | -------------- | ------------------------------------ |
| A1 | **Observable** | ✅ **concluído (baseline congelado)** |
| A2 | Identifiable   | ⬜ próximo                            |

---

## Próximo passo

Se estiver de acordo com este nível de formalismo (DbC + TDD), o próximo objeto **natural** é:

> **A2 — Identifiable**
> (grandezas **não observáveis**, inferidas, com forte carga epistêmica)

Quando quiser, diga:

**“Vamos para o Identifiable”**
