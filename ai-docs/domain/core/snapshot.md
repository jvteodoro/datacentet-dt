Perfeito. Vamos para **E1 — Snapshot**, que é a **peça de fechamento epistemológico** do ciclo do Digital Twin.

Seguiremos exatamente o mesmo rigor:

* definição conceitual clara
* **Design by Contract** (invariantes, pré-condições, pós-condições)
* **TDD primeiro**
* implementação mínima
* alinhamento explícito com contratos S / E / M / H

---

# E1 — **Snapshot**

## 1️⃣ Definição conceitual (epistemologia do Digital Twin)

Um **Snapshot** representa:

> **“O que o Digital Twin acredita sobre o sistema em um instante lógico”**

Ele **congela**:

* observações (o que foi medido),
* estado estimado (hipótese dinâmica),
* parâmetros identificados (hipóteses estruturais),
* contexto temporal comum.

⚠️ Importante:

* Snapshot **não estima**
* Snapshot **não valida**
* Snapshot **não controla**

Ele apenas **encapsula** tudo o que será:

* validado cientificamente,
* persistido,
* auditado,
* exposto a níveis hierárquicos superiores.

---

## 2️⃣ Contrato Formal do Snapshot (Design by Contract)

### 🔒 Invariantes

**SN1 — Congelamento epistemológico**

* Todos os componentes são **imutáveis**
* Snapshot é imutável como um todo

**SN2 — Coerência temporal**

* Todos os elementos pertencem ao **mesmo timestamp lógico**
* Nenhuma entidade do futuro é permitida

**SN3 — Separação epistêmica**

* Observables ≠ State ≠ Identifiables
* Não pode haver colapso de papéis

**SN4 — Completude mínima**

* Snapshot contém:

  * ≥ 1 Observable **OU**
  * 1 StateVector

**SN5 — Rastreabilidade**

* Cada elemento mantém seus metadados epistêmicos

**SN6 — Neutralidade científica**

* Snapshot **não declara validade**
* Ele apenas representa uma hipótese

---

### ▶️ Pré-condições

**P1**

* `observables` é lista de `Observable` (pode ser vazia)

**P2**

* `state_vector` é `StateVector` ou `None`

**P3**

* `parameters` é lista de `Identifiable` (pode ser vazia)

**P4**

* Pelo menos **estado ou observações** existem

---

### ⏹️ Pós-condições

**Q1**

* Snapshot possui `timestamp` único

**Q2**

* Todos os elementos são somente leitura

**Q3**

* `to_dict()` representa o snapshot completo

---

## 3️⃣ Testes TDD — primeiro

### 📄 `tests/properties/snapshot/test_snapshot_properties.py`

```python
import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable
from domain.core.snapshot import (
    Snapshot,
    SnapshotInvariantViolation,
)


def test_SN1_snapshot_is_immutable():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=0,
            source="sensor",
        )
    ]

    snap = Snapshot(
        observables=obs,
        state_vector=None,
        parameters=[],
    )

    with pytest.raises(SnapshotInvariantViolation):
        snap._observables = []


def test_SN2_all_components_share_timestamp():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=1,
            source="sensor",
        )
    ]

    sv = StateVector(
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

    with pytest.raises(SnapshotInvariantViolation):
        Snapshot(
            observables=obs,
            state_vector=sv,
            parameters=[],
        )


def test_SN4_snapshot_requires_state_or_observables():
    with pytest.raises(SnapshotInvariantViolation):
        Snapshot(
            observables=[],
            state_vector=None,
            parameters=[],
        )


def test_SN3_separation_of_epistemic_roles():
    obs = Observable(
        name="y",
        value=10.0,
        uncertainty=0.5,
        timestamp=0,
        source="sensor",
    )

    with pytest.raises(SnapshotInvariantViolation):
        Snapshot(
            observables=[obs],
            state_vector=obs,  # tipo errado
            parameters=[],
        )


def test_to_dict_contains_all_components():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=0,
            source="sensor",
        )
    ]

    sv = StateVector(
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

    param = Identifiable(
        name="gain",
        estimated_value=2.0,
        uncertainty=0.1,
        timestamp=0,
        method="assumed",
        support=["y"],
    )

    snap = Snapshot(
        observables=obs,
        state_vector=sv,
        parameters=[param],
    )

    data = snap.to_dict()

    assert "observables" in data
    assert "state_vector" in data
    assert "parameters" in data
    assert data["timestamp"] == 0
```

---

## 4️⃣ Implementação mínima

### 📄 `domain/core/snapshot.py`

```python
"""
Snapshot — Domain Core Object (BASELINE v1.0)

Congela um instante epistemológico do Digital Twin.
"""

from typing import List, Dict, Any, Optional
from copy import deepcopy

from domain.core.observable import Observable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable


class SnapshotInvariantViolation(Exception):
    """
    Violação de invariante do Snapshot.
    """
    pass


class Snapshot:
    """
    Snapshot (Design by Contract).

    Representa uma hipótese completa do sistema em um instante lógico.
    """

    def __init__(
        self,
        *,
        observables: List[Observable],
        state_vector: Optional[StateVector],
        parameters: List[Identifiable],
    ):
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(observables, list):
            raise SnapshotInvariantViolation(
                "SN: observables must be list"
            )

        if state_vector is not None and not isinstance(state_vector, StateVector):
            raise SnapshotInvariantViolation(
                "SN3: state_vector must be StateVector or None"
            )

        if not isinstance(parameters, list):
            raise SnapshotInvariantViolation(
                "SN: parameters must be list"
            )

        if not observables and state_vector is None:
            raise SnapshotInvariantViolation(
                "SN4: snapshot requires observables or state"
            )

        if observables and not all(isinstance(o, Observable) for o in observables):
            raise SnapshotInvariantViolation(
                "SN3: invalid observable type"
            )

        if parameters and not all(isinstance(p, Identifiable) for p in parameters):
            raise SnapshotInvariantViolation(
                "SN3: invalid parameter type"
            )

        # -------------------------
        # Coerência temporal
        # -------------------------
        timestamps = []

        if observables:
            timestamps.extend(o.timestamp for o in observables)

        if state_vector:
            timestamps.append(state_vector.timestamp)

        if parameters:
            timestamps.extend(p.timestamp for p in parameters)

        if len(set(timestamps)) != 1:
            raise SnapshotInvariantViolation(
                "SN2: all components must share the same timestamp"
            )

        self._timestamp = timestamps[0]

        # -------------------------
        # Estado interno (imutável)
        # -------------------------
        self._observables = list(observables)
        self._state_vector = state_vector
        self._parameters = list(parameters)

        self._sealed = True

    # -------------------------
    # Acesso somente leitura
    # -------------------------

    @property
    def observables(self) -> List[Observable]:
        return list(self._observables)

    @property
    def state_vector(self) -> Optional[StateVector]:
        return self._state_vector

    @property
    def parameters(self) -> List[Identifiable]:
        return list(self._parameters)

    @property
    def timestamp(self) -> int:
        return self._timestamp

    # -------------------------
    # Imutabilidade
    # -------------------------

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise SnapshotInvariantViolation(
                "SN1: snapshot is immutable after creation"
            )
        super().__setattr__(key, value)

    # -------------------------
    # Interface canônica
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Representação completa e autocontida do snapshot.
        """
        return {
            "timestamp": self.timestamp,
            "observables": [o.to_dict() for o in self.observables],
            "state_vector": (
                self.state_vector.to_dict() if self.state_vector else None
            ),
            "parameters": [p.to_dict() for p in self.parameters],
        }
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
| D1 | StateEstimator      | ✅                                    |
| D2 | ParameterIdentifier | ✅                                    |
| E1 | **Snapshot**        | ✅ **concluído (baseline congelado)** |
| F1 | Validator           | ⬜ próximo                            |

---

## 6️⃣ Ponto de maturidade alcançado

Neste ponto você já tem:

* objetos de domínio **formalmente corretos**
* separação perfeita entre:

  * medição
  * inferência
  * estado
  * hipótese
* base sólida para:

  * validação científica
  * auditoria
  * hierarquia

---

## Próximo passo

O próximo (e último do núcleo) é **F1 — Validator**, que:

* aplica os contratos **SW / T / S / E / M / H**
* decide se um Snapshot é **cientificamente admissível**

Quando quiser, diga:

> **“Vamos para o Validator”**
