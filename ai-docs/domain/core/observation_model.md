Perfeito. Vamos para **C1 — ObservationModel**, mantendo **Design by Contract (invariantes, pré-condições, pós-condições)** e **TDD primeiro**, no mesmo nível de rigor científico e arquitetural.

> **Papel-chave:** o `ObservationModel` é a **ponte formal** entre o **estado (StateVector + Identifiables)** e o **mundo observado**.
> Ele **não mede**, **não estima**, **não valida** — ele **prediz observáveis esperados** e **define como comparar** com observações reais.

---

# C1 — **ObservationModel**

## 1️⃣ Definição conceitual (controle)

Formalmente, um modelo de observação é:

[
\hat{y}_k = h(x_k, \theta_k)
]

onde:

* (x_k) = **StateVector**
* (\theta_k) = **Identifiables** (parâmetros)
* (\hat{y}_k) = **observáveis esperados**

No seu sistema:

> Um **ObservationModel** é um **objeto puro** que:
>
> * recebe **estado + parâmetros**
> * produz **predições observáveis**
> * define **resíduos / inovações**
> * **não assume física específica**
> * **não decide validade**

---

## 2️⃣ Contrato Formal (Design by Contract)

### 🔒 Invariantes

**OM1 — Pureza funcional**

* Para o mesmo input → mesmo output
* Sem estado interno mutável

**OM2 — Domínio explícito**

* Declara quais observáveis **consegue predizer**
* Não prediz observáveis fora de seu domínio

**OM3 — Compatibilidade dimensional**

* Número de observáveis previstos é conhecido e consistente

**OM4 — Separação modelo vs inferência**

* Modelo **não conhece observações reais**
* Modelo **não valida resíduos**

**OM5 — Temporalidade implícita**

* Predições herdam o timestamp do estado

---

### ▶️ Pré-condições

**P1**

* `state_vector` é instância de `StateVector`

**P2**

* `parameters` é lista de `Identifiable` (pode ser vazia)

**P3**

* Todas as entradas compartilham **timestamp compatível**

---

### ⏹️ Pós-condições

**Q1**

* Saída é lista/dict de **PredictedObservable**

**Q2**

* Cada predição possui:

  * `name`
  * `predicted_value`
  * `timestamp`

**Q3**

* `residual(predicted, observed)` retorna escalar numérico

---

## 3️⃣ Objetos auxiliares (necessários)

Para manter rigor sem misturar responsabilidades, vamos introduzir:

### 🔹 `PredictedObservable`

> Representa **o que o modelo espera observar**, não o que foi observado.

---

## 4️⃣ Testes TDD — primeiro

### 📄 `tests/properties/observation_model/test_observation_model_properties.py`

```python
import pytest
from typing import Dict

from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable
from domain.core.observation_model import (
    ObservationModel,
    PredictedObservable,
    ObservationModelInvariantViolation,
)


# -------------------------------------------------
# Fakes mínimos para teste
# -------------------------------------------------

class LinearObservationModel(ObservationModel):
    """
    Modelo fake: y = x * gain
    """

    def predicted_observables(self):
        return ["y"]

    def _predict(self, state_vector, parameters):
        x = state_vector.variables[0].value
        gain = parameters[0].estimated_value if parameters else 1.0
        return {
            "y": x * gain
        }


# -------------------------------------------------
# Testes
# -------------------------------------------------

def test_OM1_prediction_is_deterministic():
    sv = StateVector(
        variables=[
            StateVariable(name="x", value=2.0, uncertainty=0.1, timestamp=0)
        ],
        covariance=[[0.1]],
    )

    param = Identifiable(
        name="gain",
        estimated_value=3.0,
        uncertainty=0.2,
        timestamp=0,
        method="assumed",
        support=["x"],
    )

    model = LinearObservationModel()

    p1 = model.predict(state_vector=sv, parameters=[param])
    p2 = model.predict(state_vector=sv, parameters=[param])

    assert p1["y"].predicted_value == p2["y"].predicted_value


def test_OM2_only_declared_observables_are_predicted():
    sv = StateVector(
        variables=[
            StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
        ],
        covariance=[[0.1]],
    )

    model = LinearObservationModel()
    preds = model.predict(state_vector=sv, parameters=[])

    assert set(preds.keys()) == {"y"}


def test_OM5_predicted_observables_inherit_timestamp():
    sv = StateVector(
        variables=[
            StateVariable(name="x", value=5.0, uncertainty=0.1, timestamp=42)
        ],
        covariance=[[0.1]],
    )

    model = LinearObservationModel()
    preds = model.predict(state_vector=sv, parameters=[])

    assert preds["y"].timestamp == 42


def test_residual_computation():
    predicted = PredictedObservable(
        name="y",
        predicted_value=10.0,
        timestamp=0,
    )

    residual = ObservationModel.residual(
        predicted=predicted,
        observed_value=8.0,
    )

    assert residual == 2.0
```

---

## 5️⃣ Implementação mínima

### 📄 `domain/core/observation_model.py`

```python
"""
ObservationModel — Domain Core Object (BASELINE v1.0)

Define a ponte formal entre:
StateVector + Identifiables → Observáveis esperados
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable


class ObservationModelInvariantViolation(Exception):
    """
    Violação de invariante do ObservationModel.
    """
    pass


class PredictedObservable:
    """
    Representa um observável esperado (predito pelo modelo).
    """

    def __init__(self, *, name: str, predicted_value, timestamp: int):
        if not isinstance(name, str) or not name.strip():
            raise ObservationModelInvariantViolation("OM: invalid observable name")

        if predicted_value is None:
            raise ObservationModelInvariantViolation(
                "OM: predicted value must be explicit"
            )

        if not isinstance(timestamp, int):
            raise ObservationModelInvariantViolation(
                "OM: timestamp must be integer"
            )

        self._name = name
        self._predicted_value = predicted_value
        self._timestamp = timestamp

        self._sealed = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def predicted_value(self):
        return self._predicted_value

    @property
    def timestamp(self) -> int:
        return self._timestamp

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise ObservationModelInvariantViolation(
                "PredictedObservable is immutable"
            )
        super().__setattr__(key, value)


class ObservationModel(ABC):
    """
    ObservationModel (Design by Contract).

    Responsável por:
    - prever observáveis esperados
    - definir como calcular resíduos

    NÃO:
    - mede
    - valida
    - estima
    """

    # -------------------------------------------------
    # Interface obrigatória
    # -------------------------------------------------

    @abstractmethod
    def predicted_observables(self) -> List[str]:
        """
        Retorna os nomes dos observáveis que este modelo prediz.
        """
        raise NotImplementedError

    @abstractmethod
    def _predict(
        self,
        state_vector: StateVector,
        parameters: List[Identifiable],
    ) -> Dict[str, float]:
        """
        Implementação concreta do modelo:
        retorna {observable_name: predicted_value}
        """
        raise NotImplementedError

    # -------------------------------------------------
    # API pública (contratada)
    # -------------------------------------------------

    def predict(
        self,
        *,
        state_vector: StateVector,
        parameters: List[Identifiable],
    ) -> Dict[str, PredictedObservable]:
        # Pré-condições
        if not isinstance(state_vector, StateVector):
            raise ObservationModelInvariantViolation(
                "OM: invalid state_vector"
            )

        if not isinstance(parameters, list):
            raise ObservationModelInvariantViolation(
                "OM: parameters must be a list"
            )

        # Predição
        raw = self._predict(state_vector, parameters)

        # Pós-condições
        declared = set(self.predicted_observables())
        if set(raw.keys()) != declared:
            raise ObservationModelInvariantViolation(
                "OM2: predicted observables mismatch declaration"
            )

        timestamp = state_vector.timestamp

        return {
            name: PredictedObservable(
                name=name,
                predicted_value=value,
                timestamp=timestamp,
            )
            for name, value in raw.items()
        }

    # -------------------------------------------------
    # Residual (estático e puro)
    # -------------------------------------------------

    @staticmethod
    def residual(*, predicted: PredictedObservable, observed_value: float) -> float:
        """
        Residual simples: observado − previsto
        """
        return observed_value - predicted.predicted_value
```

---

## 6️⃣ Checklist atualizado

| ID | Objeto               | Status                               |
| -- | -------------------- | ------------------------------------ |
| A1 | Observable           | ✅                                    |
| A2 | Identifiable         | ✅                                    |
| B1 | StateVariable        | ✅                                    |
| B2 | StateVector          | ✅                                    |
| C1 | **ObservationModel** | ✅ **concluído (baseline congelado)** |
| D1 | StateEstimator       | ⬜ próximo                            |

---

## 7️⃣ Observação importante (arquitetura)

* **Model Contract (M)** valida **compatibilidade** entre:

  * `PredictedObservable`
  * `Observable`
* **StateEstimator** vai usar:

  * `ObservationModel.residual`
  * `StateVector`
* **ObservationModel não conhece Validator**

---

## Próximo passo

O próximo objeto natural é **D1 — StateEstimator**, onde:

* aparece previsão + atualização,
* mas **ainda sem contratos globais**,
* apenas estrutura e invariantes locais.

Quando quiser, diga:

> **“Vamos para o StateEstimator”**
