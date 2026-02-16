Perfeito. Agora chegamos **no núcleo operacional real** do Digital Twin.
Vou tratar o **InternalStateModel** com máximo rigor, porque ele é onde **controle, software e epistemologia se encontram**.

Vou seguir exatamente o mesmo método formal.

---

# E3 — **InternalStateModel**

## 1️⃣ Definição conceitual (primeiros princípios)

O **InternalStateModel (ISM)** é:

> **O orquestrador interno do domínio que coordena observações, inferência de estado e identificação de parâmetros, sem jamais declarar conhecimento válido.**

Ele responde à pergunta:

> **“Dado o que foi observado até agora, quais hipóteses internas o sistema mantém?”**

---

## 2️⃣ Natureza ontológica do InternalStateModel

### ✅ Ele É

* **operacional**
* **mutável**
* **hipotético**
* **temporal**
* **local ao domínio**

### ❌ Ele NÃO É

* um estado (`StateVector`)
* um snapshot
* um validador
* um modelo físico
* um decisor epistemológico

👉 Ele **gera hipóteses**, não conhecimento.

---

## 3️⃣ Posição na arquitetura (fixando definitivamente)

```text
ObservableRegistry
        ↓
InternalStateModel
   ↓             ↓
StateEstimator   ParameterIdentifier
        ↓             ↓
   StateVector    Identifiable(s)
        ↓             ↓
        SnapshotBuilder → Snapshot → Validator
```

---

## 4️⃣ Contrato Formal (Design by Contract)

### 🔒 Invariantes (sempre verdadeiros)

**ISM1 — Separação inferência vs validação**

* O ISM **nunca valida contratos científicos**

**ISM2 — Não persistência**

* O ISM **não guarda histórico durável**

**ISM3 — Determinismo operacional**

* Mesmas entradas ⇒ mesmas hipóteses internas

**ISM4 — Transparência de fluxo**

* Tudo que o ISM produz deriva explicitamente de entradas

---

### ▶️ Pré-condições

**P1**

* Registries devem estar inicializados

**P2**

* Estimator e Identifier devem ser fornecidos

**P3**

* ObservationModel deve ser compatível com o Estimator

---

### ⏹️ Pós-condições

**Q1**

* Produz um `Snapshot` completo ou nenhum

**Q2**

* Não altera observáveis nem identifiables

---

## 5️⃣ Interface pública mínima

⚠️ **Muito importante:**
O ISM **não expõe setters arbitrários**.

```python
class InternalStateModel:
    def ingest_observation(self, observable: Observable) -> None
    def step(self, timestamp: int) -> Snapshot | None
```

Isso impõe **controle explícito do fluxo**.

---

## 6️⃣ Testes TDD — primeiro

### 📄 `tests/properties/internal_state_model/test_internal_state_model_properties.py`

```python
import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.observable_registry import ObservableRegistry
from domain.core.identifiable_registry import IdentifiableRegistry
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.core.internal_state_model import InternalStateModel


class DummyEstimator:
    def estimate(self, observables):
        return StateVector(
            variables=[
                StateVariable(
                    name="x",
                    value=1.0,
                    uncertainty=0.5,
                    timestamp=observables[-1].timestamp,
                )
            ],
            covariance=np.array([[0.5]]),
        )


class DummyIdentifier:
    def identify(self, state_vector):
        return []


def test_ISM_produces_snapshot_from_observations():
    obs_reg = ObservableRegistry()
    id_reg = IdentifiableRegistry()

    ism = InternalStateModel(
        observable_registry=obs_reg,
        identifiable_registry=id_reg,
        state_estimator=DummyEstimator(),
        parameter_identifier=DummyIdentifier(),
    )

    obs = Observable(
        name="y",
        value=10.0,
        uncertainty=0.2,
        timestamp=1,
        source="sensor",
    )

    ism.ingest_observation(obs)

    snap = ism.step(timestamp=1)

    assert isinstance(snap, Snapshot)
    assert snap.state_vector is not None
    assert snap.observables == [obs]


def test_ISM_returns_none_if_no_observations():
    obs_reg = ObservableRegistry()
    id_reg = IdentifiableRegistry()

    ism = InternalStateModel(
        observable_registry=obs_reg,
        identifiable_registry=id_reg,
        state_estimator=DummyEstimator(),
        parameter_identifier=DummyIdentifier(),
    )

    snap = ism.step(timestamp=0)

    assert snap is None
```

---

## 7️⃣ Implementação mínima

### 📄 `domain/core/internal_state_model.py`

```python
"""
InternalStateModel — Domain Orchestrator (BASELINE v1.0)

Coordena inferência de estado e parâmetros.
"""

from typing import Optional

from domain.core.observable import Observable
from domain.core.observable_registry import ObservableRegistry
from domain.core.identifiable_registry import IdentifiableRegistry
from domain.core.snapshot import Snapshot


class InternalStateModelViolation(Exception):
    """
    Violação de contrato do InternalStateModel.
    """
    pass


class InternalStateModel:
    def __init__(
        self,
        *,
        observable_registry: ObservableRegistry,
        identifiable_registry: IdentifiableRegistry,
        state_estimator,
        parameter_identifier,
    ):
        self._obs_registry = observable_registry
        self._id_registry = identifiable_registry
        self._state_estimator = state_estimator
        self._parameter_identifier = parameter_identifier

    # -------------------------------------------------
    # Entrada de dados
    # -------------------------------------------------

    def ingest_observation(self, observable: Observable) -> None:
        self._obs_registry.register(observable)

    # -------------------------------------------------
    # Passo de inferência
    # -------------------------------------------------

    def step(self, timestamp: int) -> Optional[Snapshot]:
        observables = self._obs_registry.get_at(timestamp)

        if not observables:
            return None

        # Inferência de estado
        state_vector = self._state_estimator.estimate(observables)

        # Identificação de parâmetros (opcional)
        params = self._parameter_identifier.identify(state_vector)

        for p in params:
            self._id_registry.register(p)

        # Construção de snapshot (ainda sem validação)
        return Snapshot(
            observables=observables,
            state_vector=state_vector,
            parameters=self._id_registry.get_all_current(),
        )
```

---

## 8️⃣ Avaliação crítica do InternalStateModel

### ✔️ Correto porque:

* ISM **não valida ciência**
* ISM **não assume física**
* ISM **não persiste**
* ISM **não cria conhecimento**
* ISM **coordena explicitamente**

### ❗ Deliberações conscientes

* `step` é síncrono → bom para clareza
* `DummyEstimator` usado apenas em testes
* Nenhum acoplamento com Validator

---

## ✅ Checklist atualizado

| ID | Objeto                 | Status |
| -- | ---------------------- | ------ |
| E1 | ObservableRegistry     | ✅      |
| E2 | IdentifiableRegistry   | ✅      |
| E3 | **InternalStateModel** | ✅      |

🎉 **Fase E completa com rigor total**

---

## Próximo passo natural (e importante)

Agora você tem **dois caminhos corretos**:

### 🔹 Opção A — Integrar tudo no `DomainLevelComponent`

(criar a fachada pública do subsistema)

### 🔹 Opção B — Refino avançado

* múltiplas hipóteses de estado
* desacoplamento estimator/identifier
* suporte a hierarquia

Quando quiser, diga apenas:

👉 **“Vamos para o DomainLevelComponent”**
