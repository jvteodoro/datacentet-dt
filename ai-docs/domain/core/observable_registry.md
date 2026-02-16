Perfeito. Vamos tratar o **ObservableRegistry** com o **mesmo rigor formal** que usamos nos objetos anteriores, mas respeitando sua **natureza operacional** (não epistemológica, não imutável).

Vou estruturar em **6 partes**, sem pular nada.

---

# E1 — **ObservableRegistry**

## 1️⃣ Definição conceitual (papel no sistema)

O **ObservableRegistry** é um **componente operacional interno** do domínio cujo papel é:

> **Gerenciar observações ao longo do tempo e fornecer recortes coerentes dessas observações para os mecanismos de inferência.**

Ele é:

* 🟢 **mutável**
* 🟢 **temporal**
* 🟢 **operacional**
* 🔴 **não epistemológico**
* 🔴 **não persistente**
* 🔴 **não inferencial**

👉 Ele **não cria conhecimento**, apenas **organiza evidência bruta**.

---

## 2️⃣ Contrato Formal (Design by Contract)

### 🔒 Invariantes (sempre verdadeiros)

**OR1 — Homogeneidade semântica**

* O registry contém **apenas instâncias de `Observable`**

**OR2 — Coerência temporal interna**

* O registry **nunca retorna observáveis do futuro** em relação a uma consulta

**OR3 — Ordem temporal consistente**

* Observáveis são organizados por `timestamp` não decrescente

**OR4 — Não mutação epistêmica**

* O registry **nunca altera** observáveis armazenados

**OR5 — Transparência operacional**

* O registry não esconde dados nem cria dados
* O que entra é o que sai (filtrado)

---

### ▶️ Pré-condições (operações)

**P1 — Registro**

* Apenas `Observable` pode ser registrado

**P2 — Consulta**

* Timestamp de consulta deve ser `int`

---

### ⏹️ Pós-condições

**Q1**

* Observáveis registrados podem ser recuperados

**Q2**

* Consultas respeitam os limites temporais

---

## 3️⃣ Interface mínima esperada

Não vamos superdimensionar. Interface **mínima, suficiente e extensível**.

```python
class ObservableRegistry:
    def register(self, observable: Observable) -> None
    def get_at(self, timestamp: int) -> list[Observable]
    def get_since(self, timestamp: int) -> list[Observable]
    def latest_timestamp(self) -> int | None
```

---

## 4️⃣ Testes TDD — primeiro

### 📄 `tests/properties/observable_registry/test_observable_registry_properties.py`

```python
import pytest

from domain.core.observable import Observable
from domain.core.observable_registry import (
    ObservableRegistry,
    ObservableRegistryViolation,
)


def test_OR1_only_observables_can_be_registered():
    reg = ObservableRegistry()

    with pytest.raises(ObservableRegistryViolation):
        reg.register("not_an_observable")  # type: ignore


def test_OR3_observables_are_returned_in_temporal_order():
    reg = ObservableRegistry()

    o1 = Observable(
        name="y",
        value=1.0,
        uncertainty=0.1,
        timestamp=2,
        source="sensor",
    )
    o2 = Observable(
        name="y",
        value=2.0,
        uncertainty=0.1,
        timestamp=1,
        source="sensor",
    )

    reg.register(o1)
    reg.register(o2)

    obs = reg.get_since(0)

    assert [o.timestamp for o in obs] == [1, 2]


def test_OR2_registry_never_returns_future_data():
    reg = ObservableRegistry()

    o = Observable(
        name="y",
        value=5.0,
        uncertainty=0.2,
        timestamp=10,
        source="sensor",
    )

    reg.register(o)

    obs = reg.get_at(timestamp=5)

    assert obs == []


def test_get_at_returns_only_matching_timestamp():
    reg = ObservableRegistry()

    o1 = Observable(
        name="y",
        value=1.0,
        uncertainty=0.1,
        timestamp=1,
        source="sensor",
    )
    o2 = Observable(
        name="y",
        value=2.0,
        uncertainty=0.1,
        timestamp=2,
        source="sensor",
    )

    reg.register(o1)
    reg.register(o2)

    obs = reg.get_at(2)

    assert obs == [o2]


def test_latest_timestamp():
    reg = ObservableRegistry()

    assert reg.latest_timestamp() is None

    reg.register(
        Observable(
            name="y",
            value=1.0,
            uncertainty=0.1,
            timestamp=3,
            source="sensor",
        )
    )

    assert reg.latest_timestamp() == 3
```

---

## 5️⃣ Implementação mínima

### 📄 `domain/core/observable_registry.py`

```python
"""
ObservableRegistry — Domain Internal Component (BASELINE v1.0)

Gerencia observações ao longo do tempo.
"""

from typing import List, Optional

from domain.core.observable import Observable


class ObservableRegistryViolation(Exception):
    """
    Violação de contrato do ObservableRegistry.
    """
    pass


class ObservableRegistry:
    """
    Registry operacional de observáveis.

    NÃO:
    - infere
    - valida ciência
    - persiste
    """

    def __init__(self):
        self._observables: List[Observable] = []

    # -------------------------------------------------
    # Registro
    # -------------------------------------------------

    def register(self, observable: Observable) -> None:
        if not isinstance(observable, Observable):
            raise ObservableRegistryViolation(
                "OR1: only Observable instances can be registered"
            )

        # Não muta observável, apenas armazena
        self._observables.append(observable)

        # Mantém ordenação temporal
        self._observables.sort(key=lambda o: o.timestamp)

    # -------------------------------------------------
    # Consultas
    # -------------------------------------------------

    def get_at(self, timestamp: int) -> List[Observable]:
        if not isinstance(timestamp, int):
            raise ObservableRegistryViolation(
                "OR2: timestamp must be integer"
            )

        return [
            o for o in self._observables
            if o.timestamp == timestamp
        ]

    def get_since(self, timestamp: int) -> List[Observable]:
        if not isinstance(timestamp, int):
            raise ObservableRegistryViolation(
                "OR2: timestamp must be integer"
            )

        return [
            o for o in self._observables
            if o.timestamp >= timestamp
        ]

    def latest_timestamp(self) -> Optional[int]:
        if not self._observables:
            return None
        return self._observables[-1].timestamp
```

---

## 6️⃣ Avaliação crítica do design

### ✔️ O que está correto

* Registry é **simples**
* Registry é **determinístico**
* Registry não tem dependências perigosas
* Registry não conhece:

  * estado
  * estimador
  * snapshot
  * validator

### ❗ O que deliberadamente NÃO fizemos

* Não usamos heap / árvore → premature optimization
* Não criamos janelas deslizantes ainda
* Não filtramos por nome/fonte (pode vir depois)

Tudo isso pode ser **extensão**, não baseline.

---

## ✅ Checklist atualizado

| ID | Objeto                 | Status      |
| -- | ---------------------- | ----------- |
| E1 | **ObservableRegistry** | ✅ concluído |
| E2 | IdentifiableRegistry   | ⬜ próximo   |
| E3 | InternalStateModel     | ⬜ depois    |

---

## Próximo passo

O próximo objeto natural é:

👉 **IdentifiableRegistry**
(com foco em versionamento temporal e substituição segura)

Quando quiser, diga:
**“Vamos para o IdentifiableRegistry”**
