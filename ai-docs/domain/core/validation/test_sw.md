Perfeito. Vamos escrever **`test_validator_sw.py`** de forma **profissional, mínima e rigorosa**, exatamente como combinamos:

* testar **somente invariantes emergentes de Software (SW)**
* **não repetir validações locais**
* **não usar Hypothesis aqui** (estes são testes estruturais determinísticos)
* cada teste introduz **uma única violação**
* o `Validator` é exercitado **pela API pública**

---

# 📄 `tests/properties/validator/test_validator_sw.py`

```python
import pytest
import numpy as np

from domain.validation.validator import Validator
from domain.core.snapshot import Snapshot
from domain.core.observable import Observable
from domain.core.identifiable import Identifiable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector


# -------------------------------------------------
# Helpers válidos
# -------------------------------------------------

def valid_observable(timestamp=0):
    return Observable(
        name="voltage",
        value=230.0,
        uncertainty=1.0,
        timestamp=timestamp,
        source="sensor",
    )


def valid_state_vector(timestamp=0):
    return StateVector(
        variables=[
            StateVariable(
                name="v",
                value=230.0,
                uncertainty=1.0,
                timestamp=timestamp,
            )
        ],
        covariance=np.array([[1.0]]),
    )


def valid_identifiable(timestamp=0):
    return Identifiable(
        name="line_resistance",
        estimated_value=0.5,
        uncertainty=0.1,
        timestamp=timestamp,
        method="least_squares",
        support=["voltage"],
    )


def valid_snapshot():
    return Snapshot(
        observables=[valid_observable()],
        state_vector=valid_state_vector(),
        identifiables=[valid_identifiable()],
    )


# -------------------------------------------------
# SW-VAL-1 — Separação de responsabilidades
# -------------------------------------------------

def test_SW_validator_rejects_non_observable_in_observables():
    snapshot = valid_snapshot()

    # Introduz violação: StateVariable dentro de observables
    bad_observables = snapshot.observables + [
        StateVariable(
            name="x",
            value=1.0,
            uncertainty=0.1,
            timestamp=snapshot.timestamp,
        )
    ]

    bad_snapshot = Snapshot(
        observables=bad_observables,
        state_vector=snapshot.state_vector,
        identifiables=snapshot.identifiables,
    )

    result = Validator().validate(snapshot=bad_snapshot)

    assert not result.is_valid
    assert "Software" in result.violations
    assert any("observables" in msg for msg in result.violations["Software"])


def test_SW_validator_rejects_non_identifiable_in_identifiables():
    snapshot = valid_snapshot()

    # Introduz violação: Observable dentro de identifiables
    bad_identifiables = snapshot.identifiables + [
        valid_observable(timestamp=snapshot.timestamp)
    ]

    bad_snapshot = Snapshot(
        observables=snapshot.observables,
        state_vector=snapshot.state_vector,
        identifiables=bad_identifiables,
    )

    result = Validator().validate(snapshot=bad_snapshot)

    assert not result.is_valid
    assert "Software" in result.violations
    assert any("identifiables" in msg for msg in result.violations["Software"])


def test_SW_validator_rejects_non_statevariable_in_state_vector():
    snapshot = valid_snapshot()

    # Introduz violação: Identifiable dentro do state_vector
    bad_state_vector = StateVector(
        variables=[
            snapshot.state_vector.variables[0],
            Identifiable(
                name="bad",
                estimated_value=1.0,
                uncertainty=0.1,
                timestamp=snapshot.timestamp,
                method="test",
                support=["voltage"],
            ),
        ],
        covariance=np.array([[1.0, 0.0], [0.0, 1.0]]),
    )

    bad_snapshot = Snapshot(
        observables=snapshot.observables,
        state_vector=bad_state_vector,
        identifiables=snapshot.identifiables,
    )

    result = Validator().validate(snapshot=bad_snapshot)

    assert not result.is_valid
    assert "Software" in result.violations
    assert any("state vector" in msg.lower() for msg in result.violations["Software"])


# -------------------------------------------------
# SW-VAL-OK — Snapshot estruturalmente válido
# -------------------------------------------------

def test_SW_validator_accepts_structurally_valid_snapshot():
    snapshot = valid_snapshot()

    result = Validator().validate(snapshot=snapshot)

    assert result.is_valid
    assert result.violations == {}
```

---

# 🧠 Por que esses testes estão corretos

✔ Testam **somente** SW emergente
✔ Não repetem invariantes já garantidos em construtores
✔ Exercitam **Validator.validate**, nunca métodos privados
✔ Cada teste introduz **uma única violação clara**
✔ As mensagens não são “hardcoded” — só verificamos categoria e intenção

---

# 📌 O que **não** foi testado (corretamente)

❌ Imutabilidade de objetos
❌ Tipos básicos
❌ Nomes / versões
❌ Covariância válida

Tudo isso já foi testado **no nível certo**, antes.

---

## Próximo passo

👉 Se você rodar esses testes agora, o resultado esperado é:

```
test_validator_sw.py .... PASSED
```

Quando confirmar, seguimos imediatamente para:

> **`test_validator_temporal.py`**

É só dizer.
