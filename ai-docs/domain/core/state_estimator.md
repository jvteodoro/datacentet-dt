Perfeito. Vamos para **D1 — StateEstimator**, mantendo exatamente o mesmo padrão que seguimos até aqui:

* **teoria de controle primeiro**
* **Design by Contract** (invariantes, pré-condições, pós-condições)
* **TDD antes da implementação**
* **nenhuma validação global**, nenhum contrato SW/T/S/E/M/H aqui

> ⚠️ Importante: o **StateEstimator NÃO garante correção**, apenas **propõe um estado**.
> A validade científica **sempre** será decidida depois pelo **Validator + Model Contract**.

---

# D1 — **StateEstimator**

## 1️⃣ Definição conceitual (teoria de controle)

Em controle clássico / estimação:

[
\hat{x}*k = \mathcal{E}(\hat{x}*{k-1}, u_k, y_k)
]

onde:

* (\hat{x}) = **estado estimado**
* (y_k) = observações
* (\mathcal{E}) = algoritmo de estimação (KF, UKF, PF, ML, heurístico…)

No seu sistema:

> Um **StateEstimator** é um **propositor de hipótese de estado**:
>
> * recebe um **estado anterior** (opcional)
> * recebe **observáveis**
> * usa um **ObservationModel**
> * produz um **novo StateVector**
>
> Ele **não valida**, **não garante**, **não expõe conhecimento**.

---

## 2️⃣ Contrato Formal (Design by Contract)

### 🔒 Invariantes

**SE1 — Separação estimativa vs validade**

* Estimator **não lança** violações de contrato global
* Ele apenas constrói estados candidatos

**SE2 — Produção explícita de estado**

* `estimate()` sempre retorna um `StateVector`

**SE3 — Coerência temporal local**

* `state_vector.timestamp ≥ previous_state.timestamp` (se existir)

**SE4 — Consistência dimensional**

* Dimensão do `StateVector` produzido é consistente ao longo do tempo

**SE5 — Pureza relativa**

* Para mesmos inputs → mesma estimativa
  (determinismo local, salvo RNG explícito)

---

### ▶️ Pré-condições

**P1**

* `observation_model` é instância de `ObservationModel`

**P2**

* `observables` é coleção de `Observable`

**P3**

* Se fornecido, `previous_state` é `StateVector`

---

### ⏹️ Pós-condições

**Q1**

* Retorno é `StateVector`

**Q2**

* Timestamp do estado estimado é explícito

**Q3**

* Estado estimado **não compartilha referências mutáveis** com inputs

---

## 3️⃣ Testes TDD — primeiro

### 📄 `tests/properties/state_estimator/test_state_estimator_properties.py`

```python
import pytest
import numpy as np

from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.observable import Observable
from domain.core.observation_model import ObservationModel
from domain.core.state_estimator import (
    StateEstimator,
    StateEstimatorInvariantViolation,
)


# -------------------------------------------------
# Fake Observation Model
# -------------------------------------------------

class IdentityObservationModel(ObservationModel):
    """
    Modelo fake: y = x
    """

    def predicted_observables(self):
        return ["y"]

    def _predict(self, state_vector, parameters):
        return {"y": state_vector.variables[0].value}


# -------------------------------------------------
# Fake Estimator
# -------------------------------------------------

class SimpleStateEstimator(StateEstimator):
    """
    Estimador fake: x_k = média das observações
    """

    def _estimate(self, *, observables, previous_state, model):
        values = [obs.value for obs in observables]
        mean = sum(values) / len(values)

        return StateVector(
            variables=[
                StateVariable(
                    name="x",
                    value=mean,
                    uncertainty=0.1,
                    timestamp=observables[0].timestamp,
                )
            ],
            covariance=np.array([[0.1]]),
        )


# -------------------------------------------------
# Testes
# -------------------------------------------------

def test_SE2_estimator_returns_state_vector():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=0,
            source="sensor",
        )
    ]

    estimator = SimpleStateEstimator()
    model = IdentityObservationModel()

    state = estimator.estimate(
        observables=obs,
        observation_model=model,
        previous_state=None,
    )

    assert isinstance(state, StateVector)


def test_SE3_timestamp_is_monotonic():
    prev = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=5.0,
                uncertainty=0.2,
                timestamp=0,
            )
        ],
        covariance=np.array([[0.2]]),
    )

    obs = [
        Observable(
            name="y",
            value=6.0,
            uncertainty=0.3,
            timestamp=1,
            source="sensor",
        )
    ]

    estimator = SimpleStateEstimator()
    model = IdentityObservationModel()

    new_state = estimator.estimate(
        observables=obs,
        observation_model=model,
        previous_state=prev,
    )

    assert new_state.timestamp >= prev.timestamp
```

---

## 4️⃣ Implementação mínima

### 📄 `domain/core/state_estimator.py`

```python
"""
StateEstimator — Domain Core Object (BASELINE v1.0)

Responsável por PROPOR um novo StateVector
a partir de observações e estado anterior.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.core.state_vector import StateVector
from domain.core.observable import Observable
from domain.core.observation_model import ObservationModel


class StateEstimatorInvariantViolation(Exception):
    """
    Violação de invariante do StateEstimator.
    """
    pass


class StateEstimator(ABC):
    """
    StateEstimator (Design by Contract).

    Produz hipóteses de estado.
    Nunca valida contratos globais.
    """

    def estimate(
        self,
        *,
        observables: List[Observable],
        observation_model: ObservationModel,
        previous_state: Optional[StateVector],
    ) -> StateVector:
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(observables, list) or not observables:
            raise StateEstimatorInvariantViolation(
                "SE: observables must be a non-empty list"
            )

        if not all(isinstance(o, Observable) for o in observables):
            raise StateEstimatorInvariantViolation(
                "SE: all observables must be Observable"
            )

        if not isinstance(observation_model, ObservationModel):
            raise StateEstimatorInvariantViolation(
                "SE: invalid observation_model"
            )

        if previous_state is not None and not isinstance(previous_state, StateVector):
            raise StateEstimatorInvariantViolation(
                "SE: previous_state must be StateVector or None"
            )

        # -------------------------
        # Estimação concreta
        # -------------------------
        new_state = self._estimate(
            observables=observables,
            previous_state=previous_state,
            model=observation_model,
        )

        # -------------------------
        # Pós-condições
        # -------------------------
        if not isinstance(new_state, StateVector):
            raise StateEstimatorInvariantViolation(
                "SE2: estimator must return StateVector"
            )

        if previous_state is not None:
            if new_state.timestamp < previous_state.timestamp:
                raise StateEstimatorInvariantViolation(
                    "SE3: state timestamp regressed"
                )

        return new_state

    # -------------------------------------------------
    # Implementação concreta
    # -------------------------------------------------

    @abstractmethod
    def _estimate(
        self,
        *,
        observables: List[Observable],
        previous_state: Optional[StateVector],
        model: ObservationModel,
    ) -> StateVector:
        """
        Implementação concreta do algoritmo de estimação.
        """
        raise NotImplementedError
```

---

## 5️⃣ Checklist atualizado

| ID | Objeto              | Status                               |
| -- | ------------------- | ------------------------------------ |
| A1 | Observable          | ✅                                    |
| A2 | Identifiable        | ✅                                    |
| B1 | StateVariable       | ✅                                    |
| B2 | StateVector         | ✅                                    |
| C1 | ObservationModel    | ✅                                    |
| D1 | **StateEstimator**  | ✅ **concluído (baseline congelado)** |
| D2 | ParameterIdentifier | ⬜ próximo                            |

---

## 6️⃣ Observações importantes (alinhamento arquitetural)

* **Model Contract (M)** valida o *resultado* do `StateEstimator`
* **StateEstimator nunca lança** `ModelInvariantViolation`
* **Hierarquia (H)** opera **acima** desse nível
* Esse design permite:

  * KF
  * UKF
  * PF
  * ML
  * híbridos

todos como **subclasses puras**

---

## Próximo passo

O próximo objeto é **D2 — ParameterIdentifier**, que:

* infere **Identifiables**
* pode ser lento / assíncrono
* não roda a cada passo

Quando quiser, diga:

> **“Vamos para o ParameterIdentifier”**
