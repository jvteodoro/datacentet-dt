Perfeito. Vamos para **D2 — ParameterIdentifier**, fechando o **núcleo de inferência** do seu Digital Twin com o mesmo rigor:

* **teoria de controle + identificação**
* **Design by Contract** (invariantes, pré-condições, pós-condições)
* **TDD antes da implementação**
* **sem validação global** (isso é papel do Validator)

> ⚠️ Papel claro: o **ParameterIdentifier NÃO estima estado**.
> Ele **infere parâmetros (Identifiables)** a partir de dados, histórico e hipóteses.

---

# D2 — **ParameterIdentifier**

## 1️⃣ Definição conceitual (identificação de sistemas)

Em identificação clássica:

[
\hat{\theta}*k = \mathcal{I}(Y*{0:k}, X_{0:k})
]

onde:

* (\theta) = parâmetros do modelo
* (Y) = observações
* (X) = estados (opcional)
* (\mathcal{I}) = algoritmo de identificação (LS, RLS, ML, Bayesian, NN…)

No seu sistema:

> Um **ParameterIdentifier**:
>
> * consome **observáveis** e/ou **estado**
> * produz **Identifiables**
> * **não roda necessariamente a cada passo**
> * **não garante validade científica**
> * apenas **propõe parâmetros**

---

## 2️⃣ Contrato Formal (Design by Contract)

### 🔒 Invariantes

**PI1 — Separação parâmetro vs estado**

* Nunca retorna `StateVariable` ou `StateVector`

**PI2 — Produção explícita de Identifiables**

* `identify()` retorna **lista não vazia** de `Identifiable`

**PI3 — Coerência temporal**

* Timestamp dos parâmetros ≤ timestamp dos dados usados

**PI4 — Epistemicidade correta**

* Todo parâmetro produzido tem `epistemic_type == "inferred"`

**PI5 — Pureza relativa**

* Mesmo input → mesmo output
  (exceto RNG explícito)

---

### ▶️ Pré-condições

**P1**

* `observables` é lista de `Observable` (pode ser vazia)

**P2**

* `state_vector` é `StateVector` ou `None`

**P3**

* Pelo menos **uma fonte de dados** existe (observáveis ou estado)

---

### ⏹️ Pós-condições

**Q1**

* Retorno é `list[Identifiable]`

**Q2**

* Cada Identifiable possui:

  * método explícito
  * suporte explícito
  * timestamp explícito

**Q3**

* Nenhuma referência mutável compartilhada com inputs

---

## 3️⃣ Testes TDD — primeiro

### 📄 `tests/properties/parameter_identifier/test_parameter_identifier_properties.py`

```python
import pytest

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable
from domain.core.parameter_identifier import (
    ParameterIdentifier,
    ParameterIdentifierInvariantViolation,
)


# -------------------------------------------------
# Fake Identifier
# -------------------------------------------------

class ConstantGainIdentifier(ParameterIdentifier):
    """
    Identificador fake: retorna ganho constante
    """

    def _identify(self, *, observables, state_vector):
        ts = None
        if observables:
            ts = observables[0].timestamp
        elif state_vector:
            ts = state_vector.timestamp

        return [
            Identifiable(
                name="gain",
                estimated_value=2.0,
                uncertainty=0.1,
                timestamp=ts,
                method="constant_assumption",
                support=["y"],
            )
        ]


# -------------------------------------------------
# Testes
# -------------------------------------------------

def test_PI2_identifier_returns_identifiables():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=0,
            source="sensor",
        )
    ]

    identifier = ConstantGainIdentifier()

    params = identifier.identify(
        observables=obs,
        state_vector=None,
    )

    assert isinstance(params, list)
    assert all(isinstance(p, Identifiable) for p in params)


def test_PI3_parameter_timestamp_not_from_future():
    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=5.0,
                uncertainty=0.2,
                timestamp=3,
            )
        ],
        covariance=[[0.2]],
    )

    identifier = ConstantGainIdentifier()

    params = identifier.identify(
        observables=[],
        state_vector=sv,
    )

    assert params[0].timestamp <= sv.timestamp


def test_PI1_identifier_does_not_return_state():
    identifier = ConstantGainIdentifier()

    with pytest.raises(ParameterIdentifierInvariantViolation):
        identifier._validate_output([StateVariable(
            name="x", value=1.0, uncertainty=0.1, timestamp=0
        )])
```

---

## 4️⃣ Implementação mínima

### 📄 `domain/core/parameter_identifier.py`

```python
"""
ParameterIdentifier — Domain Core Object (BASELINE v1.0)

Responsável por PROPOR parâmetros identificáveis (Identifiables)
a partir de dados e/ou estado.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.core.observable import Observable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable


class ParameterIdentifierInvariantViolation(Exception):
    """
    Violação de invariante do ParameterIdentifier.
    """
    pass


class ParameterIdentifier(ABC):
    """
    ParameterIdentifier (Design by Contract).

    Produz hipóteses de parâmetros do modelo.
    Nunca produz estado.
    """

    def identify(
        self,
        *,
        observables: List[Observable],
        state_vector: Optional[StateVector],
    ) -> List[Identifiable]:
        # -------------------------
        # Pré-condições
        # -------------------------
        if not isinstance(observables, list):
            raise ParameterIdentifierInvariantViolation(
                "PI: observables must be a list"
            )

        if state_vector is not None and not isinstance(state_vector, StateVector):
            raise ParameterIdentifierInvariantViolation(
                "PI: state_vector must be StateVector or None"
            )

        if not observables and state_vector is None:
            raise ParameterIdentifierInvariantViolation(
                "PI: at least one data source required"
            )

        # -------------------------
        # Identificação concreta
        # -------------------------
        params = self._identify(
            observables=observables,
            state_vector=state_vector,
        )

        # -------------------------
        # Pós-condições / invariantes
        # -------------------------
        self._validate_output(params, observables, state_vector)

        return params

    # -------------------------------------------------
    # Validação local
    # -------------------------------------------------

    def _validate_output(
        self,
        params,
        observables,
        state_vector,
    ):
        if not isinstance(params, list) or not params:
            raise ParameterIdentifierInvariantViolation(
                "PI2: must return non-empty list of Identifiable"
            )

        for p in params:
            if not isinstance(p, Identifiable):
                raise ParameterIdentifierInvariantViolation(
                    "PI1: identifier cannot return non-Identifiable objects"
                )

            if p.timestamp is None:
                raise ParameterIdentifierInvariantViolation(
                    "PI3: identifiable must have timestamp"
                )

            if observables:
                max_ts = max(o.timestamp for o in observables)
                if p.timestamp > max_ts:
                    raise ParameterIdentifierInvariantViolation(
                        "PI3: parameter timestamp from future (observables)"
                    )

            if state_vector:
                if p.timestamp > state_vector.timestamp:
                    raise ParameterIdentifierInvariantViolation(
                        "PI3: parameter timestamp from future (state)"
                    )

    # -------------------------------------------------
    # Implementação concreta
    # -------------------------------------------------

    @abstractmethod
    def _identify(
        self,
        *,
        observables: List[Observable],
        state_vector: Optional[StateVector],
    ) -> List[Identifiable]:
        """
        Implementação concreta do algoritmo de identificação.
        """
        raise NotImplementedError
```

---

## 5️⃣ Checklist atualizado

| ID | Objeto                  | Status                               |
| -- | ----------------------- | ------------------------------------ |
| A1 | Observable              | ✅                                    |
| A2 | Identifiable            | ✅                                    |
| B1 | StateVariable           | ✅                                    |
| B2 | StateVector             | ✅                                    |
| C1 | ObservationModel        | ✅                                    |
| D1 | StateEstimator          | ✅                                    |
| D2 | **ParameterIdentifier** | ✅ **concluído (baseline congelado)** |
| E1 | Snapshot                | ⬜ próximo                            |

---

## 6️⃣ Observação arquitetural crucial

Agora você tem **separação perfeita**:

| Papel             | Responsável             |
| ----------------- | ----------------------- |
| Medir             | Observable              |
| Inferir parâmetro | ParameterIdentifier     |
| Estimar estado    | StateEstimator          |
| Prever observação | ObservationModel        |
| Validar ciência   | Validator (virá depois) |

Isso permite:

* pipelines assíncronos
* modelos híbridos
* ML plugável
* auditoria científica

---

## Próximo passo

O próximo objeto natural é **E1 — Snapshot**, que:

* captura **estado + parâmetros + observáveis**
* congela um instante epistemicamente válido
* alimenta o Validator e Persistência

Quando quiser, diga:

> **“Vamos para o Snapshot”**
