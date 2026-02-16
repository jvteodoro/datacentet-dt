Perfeito. Agora entramos no **coração formal da teoria de controle** do seu Digital Twin.

Vamos tratar o **B2 — StateVector** com o mesmo rigor:
**Design by Contract (invariantes, pré-condições, pós-condições) + TDD primeiro**, e **sem vazar responsabilidades** para estimadores ou modelos.

Vou seguir exatamente esta ordem:

1️⃣ Definição conceitual
2️⃣ Contrato formal (invariantes, pré, pós)
3️⃣ Testes TDD
4️⃣ Implementação mínima
5️⃣ Checklist atualizado
6️⃣ Observações importantes (ligação com Model Contract)

---

# B2 — **StateVector**

## 1️⃣ Definição conceitual (teoria de controle)

Em teoria de controle:

[
\mathbf{x}_k =
\begin{bmatrix}
x_1(k) \
x_2(k) \
\vdots \
x_n(k)
\end{bmatrix}
]

Mas no **seu sistema**, isso **não é apenas um array numérico**.

> Um **StateVector** é uma **entidade semântica composta**, que:
>
> • agrega variáveis de estado
> • preserva contexto temporal comum
> • carrega incerteza conjunta
> • representa a **hipótese atual** sobre o sistema

Ele:

* **não estima**
* **não propaga**
* **não valida**
* apenas **representa o estado assumido**

---

## 2️⃣ Contrato Formal do StateVector (Design by Contract)

### 🔒 Invariantes (sempre verdadeiros)

**SVEC1 — Composição válida**

* Contém **uma ou mais** `StateVariable`
* Todas são instâncias válidas de `StateVariable`

**SVEC2 — Identidade única das variáveis**

* Não pode haver duas variáveis com o mesmo `name`

**SVEC3 — Consistência temporal**

* Todas as `StateVariable.timestamp` são **iguais**
* O vetor tem **um único timestamp**

**SVEC4 — Incerteza composta explícita**

* Existe uma **covariância** associada ao vetor
* Covariância é:

  * matriz quadrada
  * simétrica
  * semidefinida positiva
  * dimensão compatível com o número de variáveis

**SVEC5 — Epistemicidade correta**

* `epistemic_type == "state_vector"`

**SVEC6 — Imutabilidade**

* Após criação, o vetor **não pode ser mutado**

---

### ▶️ Pré-condições

**P1**

* Lista de variáveis não vazia

**P2**

* Todas as variáveis são `StateVariable`

**P3**

* Nomes das variáveis são únicos

**P4**

* Covariância compatível com `len(variables)`

---

### ⏹️ Pós-condições

**Q1**

* O vetor expõe as variáveis exatamente como fornecidas

**Q2**

* `timestamp` do vetor = timestamp das variáveis

**Q3**

* `to_dict()` representa o estado de forma autocontida

**Q4**

* O vetor é imutável

---

## 3️⃣ Testes TDD — primeiro

### 📄 `tests/properties/state_vector/test_state_vector_properties.py`

```python
import pytest
import numpy as np
from hypothesis import given, strategies as st

from domain.core.state_variable import StateVariable
from domain.core.state_vector import (
    StateVector,
    StateVectorInvariantViolation,
)

# -------------------------------------------------
# Estratégias
# -------------------------------------------------

valid_names = st.text(min_size=1)
valid_values = st.floats(allow_nan=False, allow_infinity=False)
valid_uncertainty = st.floats(min_value=0, allow_nan=False, allow_infinity=False)
valid_timestamp = st.integers()

@st.composite
def state_variables(draw, size=st.integers(min_value=1, max_value=5)):
    n = draw(size)
    timestamp = draw(valid_timestamp)
    names = draw(st.lists(valid_names, min_size=n, max_size=n, unique=True))

    variables = []
    for name in names:
        variables.append(
            StateVariable(
                name=name,
                value=draw(valid_values),
                uncertainty=draw(valid_uncertainty),
                timestamp=timestamp,
            )
        )
    return variables

@st.composite
def valid_covariance(draw, dim):
    mat = draw(
        st.lists(
            st.lists(st.floats(min_value=0, max_value=1), min_size=dim, max_size=dim),
            min_size=dim,
            max_size=dim,
        )
    )
    cov = np.array(mat)
    return cov @ cov.T  # garante semidefinida positiva


# -------------------------------------------------
# Invariantes estruturais
# -------------------------------------------------

@given(variables=state_variables())
def test_SVEC1_to_SVEC3_valid_state_vector_is_created(variables):
    dim = len(variables)
    cov = np.eye(dim)

    sv = StateVector(
        variables=variables,
        covariance=cov,
    )

    assert len(sv.variables) == dim
    assert sv.timestamp == variables[0].timestamp


def test_SVEC2_variable_names_must_be_unique():
    v1 = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    v2 = StateVariable(name="x", value=2.0, uncertainty=0.2, timestamp=0)

    with pytest.raises(StateVectorInvariantViolation):
        StateVector(
            variables=[v1, v2],
            covariance=np.eye(2),
        )


def test_SVEC3_all_variables_must_share_timestamp():
    v1 = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    v2 = StateVariable(name="y", value=2.0, uncertainty=0.2, timestamp=1)

    with pytest.raises(StateVectorInvariantViolation):
        StateVector(
            variables=[v1, v2],
            covariance=np.eye(2),
        )


@given(variables=state_variables())
def test_SVEC4_covariance_dimension_must_match(variables):
    dim = len(variables)

    with pytest.raises(StateVectorInvariantViolation):
        StateVector(
            variables=variables,
            covariance=np.eye(dim + 1),
        )


def test_SVEC6_state_vector_is_immutable():
    v = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    sv = StateVector(variables=[v], covariance=np.eye(1))

    with pytest.raises(StateVectorInvariantViolation):
        sv._variables = []


def test_SVEC5_epistemic_type_is_state_vector():
    v = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    sv = StateVector(variables=[v], covariance=np.eye(1))

    data = sv.to_dict()
    assert data["epistemic_type"] == "state_vector"
```

---

## 4️⃣ Implementação mínima

### 📄 `domain/core/state_vector.py`

```python
"""
StateVector — Domain Core Object (BASELINE v1.0)

Representa o vetor de estado do sistema em um instante lógico.
"""

import numpy as np
from typing import List, Dict, Any
from copy import deepcopy

from domain.core.state_variable import StateVariable


class StateVectorInvariantViolation(Exception):
    """
    Violação de invariante do StateVector.
    """
    pass


class StateVector:
    """
    StateVector (Design by Contract).

    Agrega múltiplas StateVariable em um estado composto,
    com incerteza conjunta explícita.
    """

    def __init__(
        self,
        *,
        variables: List[StateVariable],
        covariance: np.ndarray,
    ):
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(variables, list) or not variables:
            raise StateVectorInvariantViolation(
                "SVEC1: variables must be a non-empty list"
            )

        if not all(isinstance(v, StateVariable) for v in variables):
            raise StateVectorInvariantViolation(
                "SVEC1: all elements must be StateVariable"
            )

        names = [v.name for v in variables]
        if len(names) != len(set(names)):
            raise StateVectorInvariantViolation(
                "SVEC2: variable names must be unique"
            )

        timestamps = {v.timestamp for v in variables}
        if len(timestamps) != 1:
            raise StateVectorInvariantViolation(
                "SVEC3: all variables must share the same timestamp"
            )

        if not isinstance(covariance, np.ndarray):
            raise StateVectorInvariantViolation(
                "SVEC4: covariance must be numpy array"
            )

        dim = len(variables)
        if covariance.shape != (dim, dim):
            raise StateVectorInvariantViolation(
                "SVEC4: covariance dimension mismatch"
            )

        if not np.allclose(covariance, covariance.T):
            raise StateVectorInvariantViolation(
                "SVEC4: covariance must be symmetric"
            )

        eigvals = np.linalg.eigvals(covariance)
        if (eigvals < -1e-8).any():
            raise StateVectorInvariantViolation(
                "SVEC4: covariance must be positive semidefinite"
            )

        # -------------------------
        # Estado interno (imutável)
        # -------------------------
        self._variables = list(variables)
        self._covariance = covariance.copy()
        self._timestamp = variables[0].timestamp

        self._sealed = True

    # -------------------------
    # Acesso somente leitura
    # -------------------------

    @property
    def variables(self) -> List[StateVariable]:
        return list(self._variables)

    @property
    def covariance(self) -> np.ndarray:
        return self._covariance.copy()

    @property
    def timestamp(self) -> int:
        return self._timestamp

    # -------------------------
    # Imutabilidade
    # -------------------------

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise StateVectorInvariantViolation(
                "SVEC6: state vector is immutable after creation"
            )
        super().__setattr__(key, value)

    # -------------------------
    # Interface canônica
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Representação autocontida do vetor de estado para snapshot.
        """
        return {
            "variables": [v.to_dict() for v in self.variables],
            "covariance": self.covariance,
            "timestamp": self.timestamp,
            "epistemic_type": "state_vector",
        }
```

---

## 5️⃣ Checklist atualizado

| ID | Objeto           | Status                               |
| -- | ---------------- | ------------------------------------ |
| A1 | Observable       | ✅                                    |
| A2 | Identifiable     | ✅                                    |
| B1 | StateVariable    | ✅                                    |
| B2 | **StateVector**  | ✅ **concluído (baseline congelado)** |
| C1 | ObservationModel | ⬜ próximo                            |

---

## 6️⃣ Observações importantes (alinhamento com contratos)

* **Statistical Contract (S)**
  → já está respeitado pela validação da covariância

* **Temporal Contract (T)**
  → garantido por `SVEC3`

* **Model Contract (M)**
  → este objeto é a **entidade central** que o Model Contract valida

* **Hierarchy Contract (H)**
  → agregações de `StateVector` virão depois

---

## Próximo passo

O próximo objeto é **C1 — ObservationModel**, onde:

* conectamos `StateVector + Identifiables → Observables esperados`
* surgem resíduos, inovação e compatibilidade

Quando quiser, diga:

> **“Vamos para o ObservationModel”**
