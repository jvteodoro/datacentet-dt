Perfeito. Vamos para **B1 — StateVariable**, mantendo **Design by Contract (invariantes, pré-condições e pós-condições)** e **TDD primeiro**, no mesmo nível de rigor dos anteriores.

---

# B1 — **StateVariable**

## 1️⃣ Definição conceitual (teoria de controle)

Uma **StateVariable** é uma grandeza que:

* **possui dinâmica** (memória),
* é **necessária** para prever o comportamento futuro,
* **não é, por definição, diretamente observável**,
* pode ser **estimada** e **propagada no tempo**.

> Diferente de Observable, a StateVariable **carrega memória**.
> Diferente de Identifiable, ela **faz parte do vetor de estado**.

Exemplos:

* energia acumulada,
* temperatura interna equivalente,
* carga térmica,
* estado de um capacitor/bateria.

---

## 2️⃣ Contrato Formal (Design by Contract)

### 🔒 Invariantes

**SV1 — Identidade semântica**

* `name` é `str` não vazia

**SV2 — Valor explícito**

* `value` existe (≠ `None`)

**SV3 — Incerteza explícita**

* `uncertainty ≥ 0`

**SV4 — Contexto temporal**

* `timestamp` é `int` (tempo lógico do estado)

**SV5 — Epistemicidade correta**

* `epistemic_type == "state"`

**SV6 — Memória explícita**

* `timestamp` representa o **último instante de validade** do estado

**SV7 — Imutabilidade**

* Após criação, não pode ser mutada silenciosamente

---

### ▶️ Pré-condições

**P1**

* `name` é `str` não vazia

**P2**

* `value` ≠ `None`

**P3**

* `uncertainty` é numérica e `≥ 0`

**P4**

* `timestamp` é `int`

---

### ⏹️ Pós-condições

**Q1**

* O objeto expõe exatamente os valores fornecidos

**Q2**

* `to_dict()` contém campos contratuais completos

**Q3**

* O objeto é imutável

---

## 3️⃣ Testes TDD (primeiro)

### 📄 `tests/properties/state_variable/test_state_variable_properties.py`

```python
import pytest
from hypothesis import given, strategies as st

from domain.core.state_variable import (
    StateVariable,
    StateVariableInvariantViolation,
)

# -------------------------
# Estratégias
# -------------------------

valid_names = st.text(min_size=1)
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
)
def test_SV1_to_SV6_valid_state_variable_is_created(
    name, value, uncertainty, timestamp
):
    sv = StateVariable(
        name=name,
        value=value,
        uncertainty=uncertainty,
        timestamp=timestamp,
    )

    assert sv.name == name
    assert sv.value == value
    assert sv.uncertainty == uncertainty
    assert sv.timestamp == timestamp


def test_SV3_uncertainty_must_be_non_negative():
    with pytest.raises(StateVariableInvariantViolation):
        StateVariable(
            name="energy",
            value=100.0,
            uncertainty=-0.1,
            timestamp=0,
        )


def test_SV7_state_variable_is_immutable():
    sv = StateVariable(
        name="temperature_internal",
        value=40.0,
        uncertainty=0.5,
        timestamp=10,
    )

    with pytest.raises(StateVariableInvariantViolation):
        sv._value = 42.0


def test_SV5_epistemic_type_is_state():
    sv = StateVariable(
        name="charge",
        value=0.8,
        uncertainty=0.1,
        timestamp=3,
    )

    data = sv.to_dict()
    assert data["epistemic_type"] == "state"
```

---

## 4️⃣ Implementação mínima

### 📄 `domain/core/state_variable.py`

```python
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
```

---

## 5️⃣ Checklist atualizado

| ID | Objeto            | Status                               |
| -- | ----------------- | ------------------------------------ |
| A1 | Observable        | ✅                                    |
| A2 | Identifiable      | ✅                                    |
| B1 | **StateVariable** | ✅ **concluído (baseline congelado)** |
| B2 | StateVector       | ⬜ próximo                            |

---

## Próximo passo

O próximo passo natural é **B2 — StateVector**, onde:

* múltiplas `StateVariable`s são compostas,
* surgem invariantes **estatísticos e temporais compostos**,
* começa a ligação direta com o **Model Contract (M)**.

Quando quiser, diga:

> **“Vamos para o StateVector”**
