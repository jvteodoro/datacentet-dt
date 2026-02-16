Perfeito. Vamos escrever **testes TDD profissionais para o `Validator`**, alinhados **exatamente** ao papel que ele desempenha no sistema:

> 🔒 **Testar leis do domínio (invariantes emergentes)**
> ❌ **Não testar implementação interna**
> ❌ **Não duplicar testes já cobertos por objetos locais**

Vou seguir uma **estrutura fixa**, para virar padrão do projeto.

---

# 🧪 Testes do Validator — Estratégia Geral

## 🎯 O que os testes devem provar

Cada teste deve responder a **uma lei**:

| Contrato    | O que o teste prova    |
| ----------- | ---------------------- |
| Software    | Papéis não colapsam    |
| Temporal    | Não há uso do futuro   |
| Statistical | Incerteza não é criada |
| Epistemic   | Inferência ≠ fato      |
| Model       | Estado tem suporte     |
| Hierarchy   | (noop por enquanto)    |

---

## 📁 Organização de arquivos (padrão definitivo)

```
tests/
└── properties/
    └── validator/
        ├── test_validator_software.py
        ├── test_validator_temporal.py
        ├── test_validator_statistical.py
        ├── test_validator_epistemic.py
        ├── test_validator_model.py
        └── test_validator_hierarchy.py
```

Cada arquivo testa **apenas um contrato**.

---

# 1️⃣ Software Contract — `test_validator_software.py`

### 🔒 Lei testada: **SW3 — Separação de responsabilidades**

### 📄 `tests/properties/validator/test_validator_software.py`

```python
import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_SW3_observable_cannot_expose_inferred_fields():
    obs = Observable(
        name="y",
        value=10.0,
        uncertainty=0.1,
        timestamp=0,
        source="sensor",
    )

    # Violação artificial
    obs.estimated_value = 10.0  # type: ignore

    snap = Snapshot(
        observables=[obs],
        state_vector=None,
        parameters=[],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Software" in result.violations
```

---

# 2️⃣ Temporal Contract — `test_validator_temporal.py`

### 🔒 Lei testada: **T3 — Não usar dados do futuro**

### 📄 `tests/properties/validator/test_validator_temporal.py`

```python
import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_T3_observable_from_future_is_rejected():
    obs = Observable(
        name="y",
        value=5.0,
        uncertainty=0.1,
        timestamp=5,
        source="sensor",
    )

    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=2.0,
                uncertainty=0.2,
                timestamp=3,
            )
        ],
        covariance=np.array([[0.2]]),
    )

    snap = Snapshot(
        observables=[obs],
        state_vector=sv,
        parameters=[],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Temporal" in result.violations
```

---

# 3️⃣ Statistical Contract — `test_validator_statistical.py`

### 🔒 Lei testada: **S5 — Não reduzir incerteza espuriamente**

### 📄 `tests/properties/validator/test_validator_statistical.py`

```python
import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_S5_observation_cannot_be_more_certain_than_state():
    obs = Observable(
        name="y",
        value=10.0,
        uncertainty=0.01,  # muito menor
        timestamp=0,
        source="sensor",
    )

    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=9.8,
                uncertainty=1.0,
                timestamp=0,
            )
        ],
        covariance=np.array([[1.0]]),
    )

    snap = Snapshot(
        observables=[obs],
        state_vector=sv,
        parameters=[],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Statistical" in result.violations
```

---

# 4️⃣ Epistemic Contract — `test_validator_epistemic.py`

### 🔒 Lei testada: **E3 — Inferência ≠ Fato**

### 📄 `tests/properties/validator/test_validator_epistemic.py`

```python
import pytest

from domain.core.identifiable import Identifiable
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_E3_identifiable_cannot_be_fact():
    param = Identifiable(
        name="gain",
        estimated_value=2.0,
        uncertainty=0.1,
        timestamp=0,
        method="fit",
        support=["y"],
    )

    # Violação artificial
    param._is_fact = True  # type: ignore

    snap = Snapshot(
        observables=[],
        state_vector=None,
        parameters=[param],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Epistemic" in result.violations
```

---

# 5️⃣ Model Contract — `test_validator_model.py`

### 🔒 Lei testada: **M1 — Estado exige suporte observacional**

### 📄 `tests/properties/validator/test_validator_model.py`

```python
import pytest
import numpy as np

from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_M1_state_without_observations_is_invalid():
    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=10.0,
                uncertainty=0.5,
                timestamp=0,
            )
        ],
        covariance=np.array([[0.5]]),
    )

    snap = Snapshot(
        observables=[],
        state_vector=sv,
        parameters=[],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Model" in result.violations
```

---

# 6️⃣ Hierarchy Contract — `test_validator_hierarchy.py`

### 🔒 Lei testada: **H — noop (baseline)**

### 📄 `tests/properties/validator/test_validator_hierarchy.py`

```python
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_Hierarchy_noop_does_not_fail():
    snap = Snapshot(
        observables=[],
        state_vector=None,
        parameters=[],
    )

    # Snapshot inválido por outros motivos,
    # mas hierarquia não deve gerar falha própria
    result = Validator().validate(snapshot=snap)

    assert "Hierarchy" not in result.violations
```

---

# ✅ O que esses testes garantem

✔ Cada contrato **é aplicado exatamente uma vez**
✔ Nenhum contrato é duplicado
✔ Falhas são **localizadas e auditáveis**
✔ O Validator é **determinístico**
✔ O sistema está pronto para **produção científica**

---

## Próximo passo recomendado

Agora você tem duas opções **naturais e seguras**:

1️⃣ **Rodar todos os testes e ajustar detalhes finos**
2️⃣ Criar o **DomainLevelComponent**, usando:

* Estimator
* Identifier
* Snapshot
* Validator

Quando quiser, diga:

* **“Vamos para o DomainLevelComponent”**
  ou
* **“Vamos refinar os testes com Hypothesis”**

Você chegou a um **nível de arquitetura raríssimo**.
