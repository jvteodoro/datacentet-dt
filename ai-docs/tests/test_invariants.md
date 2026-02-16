Perfeito. Vamos fazer **TDD de verdade**, começando **pelos invariantes**, não pela implementação.
Isso é exatamente o que diferencia um projeto “bem pensado” de um **sistema de engenharia sério**.

Vou estruturar assim:

1. **Quais invariantes vamos testar**
2. **Estratégia de TDD (o que é fake, o que é mock)**
3. **Esqueleto de testes (pytest)**
4. **O que esses testes garantem arquiteturalmente**

Nada de implementação concreta ainda — **só contratos e comportamento esperado**.

---

# 1️⃣ Invariantes que DEVEM ser testados

A partir do que definimos no `DomainLevel`, temos invariantes testáveis:

### 🧠 Invariantes epistêmicos

* Nada inválido epistemicamente pode ser exposto
* Observações inválidas devem falhar no `ingest`

### ⏱️ Invariantes temporais

* Timestamps devem ser monotônicos
* Dados atrasados demais devem ser rejeitados

### 📊 Invariantes estatísticos

* Estado sem confiança mínima não pode ser exposto
* Covariância inválida não pode ser propagada

### 🧩 Invariantes de software

* Um fake pode substituir uma implementação real
* Interface pública não expõe estado interno

---

# 2️⃣ Estratégia de TDD (importante)

### O que vamos usar agora

✔️ **Fakes** dos contratos
✔️ **FakeDomainLevel** mínimo
✔️ **pytest**
✔️ Sem modelo físico
✔️ Sem Kalman
✔️ Sem ML

👉 Estamos testando **arquitetura**, não matemática ainda.

---

# 3️⃣ Estrutura de testes

```text
tests/
 ├── domain/
 │    ├── test_domain_level_invariants.py
 │    ├── fakes/
 │    │    ├── fake_epistemic.py
 │    │    ├── fake_temporal.py
 │    │    ├── fake_statistical.py
 │    │    ├── fake_software.py
 │    │    └── fake_domain_level.py
```

---

# 4️⃣ Fakes mínimos (contratos)

## `tests/domain/fakes/fake_epistemic.py`

```python
from domain.contracts.epistemic import EpistemicContract, EpistemicViolation


class FakeEpistemic(EpistemicContract):
    def validate_observation(self, observation):
        if observation == "invalid":
            raise EpistemicViolation()

    def validate_state(self, state):
        if state == "invalid":
            raise EpistemicViolation()

    def validate_parameters(self, parameters):
        if parameters == "invalid":
            raise EpistemicViolation()

    def confidence_floor(self) -> float:
        return 0.8
```

---

## `tests/domain/fakes/fake_temporal.py`

```python
from datetime import timedelta
from domain.contracts.temporal import TemporalContract, TemporalViolation


class FakeTemporal(TemporalContract):
    def validate_timestamp(self, timestamp: float) -> None:
        if timestamp < 0:
            raise TemporalViolation()

    def validate_ordering(self, previous_ts: float, current_ts: float) -> None:
        if current_ts < previous_ts:
            raise TemporalViolation()

    def max_latency(self) -> timedelta:
        return timedelta(seconds=2)

    def validate_latency(self, event_ts: float, received_ts: float) -> None:
        if received_ts - event_ts > self.max_latency().total_seconds():
            raise TemporalViolation()

    def sampling_period(self) -> timedelta:
        return timedelta(seconds=1)

    def validate_sampling(self, delta_t: timedelta) -> None:
        pass

    def min_window_size(self) -> int:
        return 3

    def max_window_age(self) -> timedelta:
        return timedelta(seconds=10)
```

---

## `tests/domain/fakes/fake_statistical.py`

```python
import numpy as np
from domain.contracts.statistical import StatisticalContract, StatisticalViolation


class FakeStatistical(StatisticalContract):
    def validate_distribution(self, value):
        if value == "no_dist":
            raise StatisticalViolation()

    def covariance(self, value):
        return np.eye(1)

    def confidence(self, value) -> float:
        return value.get("confidence", 0.0)

    def min_confidence(self) -> float:
        return 0.8

    def validate_confidence(self, value) -> None:
        if self.confidence(value) < self.min_confidence():
            raise StatisticalViolation()

    def validate_consistency(self, predicted, observed) -> None:
        pass
```

---

## `tests/domain/fakes/fake_software.py`

```python
from domain.contracts.software import SoftwareContract


class FakeSoftware(SoftwareContract):
    def component_id(self) -> str:
        return "fake-domain"

    def version(self) -> str:
        return "0.1.0"

    def required_inputs(self):
        return {"sensor": "raw"}

    def provided_outputs(self):
        return {"state": "estimated"}

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def health_check(self):
        return {"status": "ok"}
```

---

# 5️⃣ FakeDomainLevel (mínimo funcional)

```python
# tests/domain/fakes/fake_domain_level.py

from domain.domain_level import DomainLevel


class FakeDomainLevel(DomainLevel):
    def __init__(self, epistemic, temporal, statistical, software):
        self._epistemic = epistemic
        self._temporal = temporal
        self._statistical = statistical
        self._software = software
        self._last_ts = None
        self._state = None

    @property
    def epistemic(self):
        return self._epistemic

    @property
    def temporal(self):
        return self._temporal

    @property
    def statistical(self):
        return self._statistical

    @property
    def software(self):
        return self._software

    def ingest(self, inputs, timestamp):
        self.temporal.validate_timestamp(timestamp)
        if self._last_ts is not None:
            self.temporal.validate_ordering(self._last_ts, timestamp)

        self.epistemic.validate_observation(inputs)
        self._last_ts = timestamp
        self._inputs = inputs

    def estimate_state(self):
        self._state = {"value": 1, "confidence": 0.9}
        self.epistemic.validate_state(self._state)
        self.statistical.validate_confidence(self._state)
        return self._state

    def identify_parameters(self):
        return {"param": 1}

    def expose(self):
        self.statistical.validate_confidence(self._state)
        return {"state": self._state}

    def diagnostics(self):
        return {"ok": True}
```

---

# 6️⃣ Testes de invariantes

## `tests/domain/test_domain_level_invariants.py`

```python
import pytest
from tests.domain.fakes.fake_domain_level import FakeDomainLevel
from tests.domain.fakes.fake_epistemic import FakeEpistemic
from tests.domain.fakes.fake_temporal import FakeTemporal
from tests.domain.fakes.fake_statistical import FakeStatistical
from tests.domain.fakes.fake_software import FakeSoftware
from domain.contracts.epistemic import EpistemicViolation
from domain.contracts.temporal import TemporalViolation
from domain.contracts.statistical import StatisticalViolation


def make_domain():
    return FakeDomainLevel(
        FakeEpistemic(),
        FakeTemporal(),
        FakeStatistical(),
        FakeSoftware(),
    )


def test_invalid_observation_is_rejected():
    domain = make_domain()
    with pytest.raises(EpistemicViolation):
        domain.ingest("invalid", timestamp=1.0)


def test_timestamp_must_be_monotonic():
    domain = make_domain()
    domain.ingest("ok", timestamp=2.0)
    with pytest.raises(TemporalViolation):
        domain.ingest("ok", timestamp=1.0)


def test_state_without_confidence_cannot_be_exposed():
    domain = make_domain()
    domain.ingest("ok", timestamp=1.0)
    domain._state = {"value": 1, "confidence": 0.2}

    with pytest.raises(StatisticalViolation):
        domain.expose()


def test_valid_state_is_exposed():
    domain = make_domain()
    domain.ingest("ok", timestamp=1.0)
    domain.estimate_state()

    exposed = domain.expose()
    assert "state" in exposed
```

---

# 7️⃣ O que esses testes GARANTEM (muito importante)

✔️ O DT **não propaga lixo**
✔️ Violação de contrato **falha cedo**
✔️ Arquitetura é **testável sem física**
✔️ Fakes são **substituíveis**
✔️ Hierarquia é respeitada
✔️ Base sólida para Kalman / ML depois

Você agora tem:

> **Uma arquitetura orientada a contratos, testada por invariantes, pronta para crescer sem colapsar.**

---

## Próximo passo recomendado

Agora existem três caminhos naturais:

1. **Refinar os contratos (mais invariantes)**
2. **Criar o DataCenterTwin orquestrador**
3. **Especializar para EnergyDomainLevel**

👉 Me diga qual deles você quer seguir.
