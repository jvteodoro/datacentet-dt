Perfeito. Vamos para o **E2 — IdentifiableRegistry**, mantendo **coerência total** com tudo que já foi alinhado:

* natureza **operacional** (não epistemológica)
* **mutável**
* **sem persistência**
* **sem validação científica**
* **governa versões e vigência** de parâmetros inferidos
* serve **exclusivamente** ao `InternalStateModel`

Vou seguir o mesmo formato rigoroso.

---

# E2 — **IdentifiableRegistry**

## 1️⃣ Definição conceitual (papel no sistema)

O **IdentifiableRegistry** é o componente responsável por:

> **Gerenciar parâmetros inferidos ao longo do tempo, garantindo que apenas versões temporalmente coerentes e semanticamente não conflitantes estejam ativas.**

Ele resolve um problema **central** em Digital Twins reais:

> *“Qual parâmetro está valendo agora?”*

---

## 2️⃣ O que o IdentifiableRegistry É (e NÃO é)

### ✅ Ele É

* um **gerenciador de versões**
* um **resolvedor de vigência**
* um **organizador de hipóteses paramétricas**
* um **buffer operacional**

### ❌ Ele NÃO É

* um identificador (não roda algoritmos)
* um validador (não aplica contratos S/E/M)
* um snapshot
* um repositório persistente

---

## 3️⃣ Contrato Formal (Design by Contract)

### 🔒 Invariantes

**IR1 — Homogeneidade semântica**

* O registry contém **apenas `Identifiable`**

**IR2 — Não conflito ativo**

* Para cada `name`, existe **no máximo um Identifiable ativo**

**IR3 — Coerência temporal interna**

* Um parâmetro mais antigo **não pode sobrescrever** um mais recente

**IR4 — Não mutação epistêmica**

* O registry **não altera** o conteúdo dos Identifiables

**IR5 — Transparência operacional**

* Parâmetros não são criados, apenas organizados

---

### ▶️ Pré-condições

**P1 — Registro**

* Apenas `Identifiable` pode ser registrado

**P2 — Consulta**

* Nome deve ser `str`

---

### ⏹️ Pós-condições

**Q1**

* O parâmetro ativo reflete a versão mais recente admissível

**Q2**

* Consultas retornam dados consistentes

---

## 4️⃣ Interface mínima esperada

```python
class IdentifiableRegistry:
    def register(self, param: Identifiable) -> None
    def get_current(self, name: str) -> Identifiable | None
    def get_all_current(self) -> list[Identifiable]
    def latest_timestamp(self) -> int | None
```

---

## 5️⃣ Testes TDD — primeiro

### 📄 `tests/properties/identifiable_registry/test_identifiable_registry_properties.py`

```python
import pytest

from domain.core.identifiable import Identifiable
from domain.core.identifiable_registry import (
    IdentifiableRegistry,
    IdentifiableRegistryViolation,
)


def make_param(name, value, ts):
    return Identifiable(
        name=name,
        estimated_value=value,
        uncertainty=0.1,
        timestamp=ts,
        method="test",
        support=["y"],
    )


def test_IR1_only_identifiables_can_be_registered():
    reg = IdentifiableRegistry()

    with pytest.raises(IdentifiableRegistryViolation):
        reg.register("not_identifiable")  # type: ignore


def test_IR2_only_one_active_per_name():
    reg = IdentifiableRegistry()

    p1 = make_param("gain", 2.0, 1)
    p2 = make_param("gain", 3.0, 2)

    reg.register(p1)
    reg.register(p2)

    current = reg.get_current("gain")

    assert current.estimated_value == 3.0


def test_IR3_older_parameter_cannot_override_newer():
    reg = IdentifiableRegistry()

    p_new = make_param("gain", 3.0, 5)
    p_old = make_param("gain", 2.0, 3)

    reg.register(p_new)
    reg.register(p_old)

    current = reg.get_current("gain")

    assert current.timestamp == 5


def test_get_all_current_returns_only_latest_versions():
    reg = IdentifiableRegistry()

    reg.register(make_param("gain", 2.0, 1))
    reg.register(make_param("offset", 1.0, 2))
    reg.register(make_param("gain", 3.0, 3))

    params = reg.get_all_current()

    names = {p.name for p in params}
    assert names == {"gain", "offset"}


def test_latest_timestamp():
    reg = IdentifiableRegistry()

    assert reg.latest_timestamp() is None

    reg.register(make_param("gain", 2.0, 4))
    reg.register(make_param("offset", 1.0, 6))

    assert reg.latest_timestamp() == 6
```

---

## 6️⃣ Implementação mínima

### 📄 `domain/core/identifiable_registry.py`

```python
"""
IdentifiableRegistry — Domain Internal Component (BASELINE v1.0)

Gerencia parâmetros inferidos e suas versões ativas.
"""

from typing import Dict, Optional, List

from domain.core.identifiable import Identifiable


class IdentifiableRegistryViolation(Exception):
    """
    Violação de contrato do IdentifiableRegistry.
    """
    pass


class IdentifiableRegistry:
    """
    Registry operacional de Identifiables.

    NÃO:
    - identifica parâmetros
    - valida ciência
    - persiste dados
    """

    def __init__(self):
        # Mapa: name -> Identifiable ativo
        self._active: Dict[str, Identifiable] = {}

    # -------------------------------------------------
    # Registro
    # -------------------------------------------------

    def register(self, param: Identifiable) -> None:
        if not isinstance(param, Identifiable):
            raise IdentifiableRegistryViolation(
                "IR1: only Identifiable instances can be registered"
            )

        name = param.name

        if name not in self._active:
            self._active[name] = param
            return

        current = self._active[name]

        # IR3: não permitir sobrescrita por versão mais antiga
        if param.timestamp < current.timestamp:
            return

        # Atualiza versão ativa
        self._active[name] = param

    # -------------------------------------------------
    # Consultas
    #-------------------------------------------------

    def get_current(self, name: str) -> Optional[Identifiable]:
        if not isinstance(name, str):
            raise IdentifiableRegistryViolation(
                "IR2: name must be string"
            )

        return self._active.get(name)

    def get_all_current(self) -> List[Identifiable]:
        return list(self._active.values())

    def latest_timestamp(self) -> Optional[int]:
        if not self._active:
            return None
        return max(p.timestamp for p in self._active.values())
```

---

## 7️⃣ Avaliação crítica do design

### ✔️ Pontos fortes

* Resolve corretamente **vigência temporal**
* Evita conflitos silenciosos
* Mantém registry **simples e previsível**
* Não vaza epistemologia

### ⚠️ Deliberações conscientes

* Não guardamos histórico completo (ainda)
* Não resolvemos conflitos semânticos (Validator faz isso)
* Não lidamos com confiança aqui (não é papel do registry)

---

## ✅ Checklist atualizado

| ID | Objeto                   | Status    |
| -- | ------------------------ | --------- |
| E1 | ObservableRegistry       | ✅         |
| E2 | **IdentifiableRegistry** | ✅         |
| E3 | InternalStateModel       | ⬜ próximo |

---

## Próximo passo (natural)

Agora sim, chegamos ao **coração operacional** do domínio:

👉 **InternalStateModel**

Ele vai:

* consumir os dois registries
* orquestrar estimador e identificador
* produzir `Snapshot`s prontos para validação

Quando quiser, diga:
**“Vamos para o InternalStateModel”**
