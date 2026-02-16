Excelente. Agora entramos no **núcleo normativo** do seu Digital Twin.

O **Validator** é o componente que **transforma hipóteses em conhecimento admissível**, aplicando **todos os contratos** que você construiu até aqui. Ele **não estima**, **não identifica**, **não controla** — ele **julga**.

Vou seguir a mesma disciplina:

1️⃣ Definição conceitual
2️⃣ Contrato formal (Design by Contract)
3️⃣ Arquitetura interna (como ele usa os contratos)
4️⃣ Testes TDD
5️⃣ Implementação mínima
6️⃣ Como ele se encaixa no sistema

---

# F1 — **Validator**

## 1️⃣ Definição conceitual (epistemologia + engenharia)

No seu sistema:

> Um **Validator** é um **árbitro científico**.
>
> Ele recebe um **Snapshot** e responde:
>
> **“Este snapshot é cientificamente admissível segundo as leis do domínio?”**

Características fundamentais:

* aplica **contratos formais** (SW, T, S, E, M, H)
* **não modifica** o snapshot
* **não decide política** (isso é do controlador)
* produz **relatório explícito de validação**

⚠️ Isso é o que separa seu sistema de:

* pipelines de dados comuns
* sistemas de monitoramento
* ML pipelines tradicionais

---

## 2️⃣ Contrato Formal do Validator (Design by Contract)

### 🔒 Invariantes

**V1 — Pureza normativa**

* Validator **não altera estado**
* Ele apenas observa e avalia

**V2 — Determinismo**

* Mesmo snapshot + mesmas regras → mesmo resultado

**V3 — Separação de contratos**

* Cada contrato é avaliado **independentemente**
* Falhas são **explicitamente atribuídas**

**V4 — Totalidade**

* Todo snapshot validado passa por **todos os contratos aplicáveis**

**V5 — Transparência**

* Resultado da validação é **auditável**
* Nenhuma falha é silenciosa

---

### ▶️ Pré-condições

**P1**

* Entrada é um `Snapshot`

**P2**

* Snapshot é imutável (contrato já garantido)

---

### ⏹️ Pós-condições

**Q1**

* Retorno é um `ValidationResult`

**Q2**

* Cada contrato avaliado gera:

  * `pass` ou `fail`
  * lista de violações (se houver)

**Q3**

* Snapshot **não é alterado**

---

## 3️⃣ Arquitetura interna do Validator

O Validator **não reimplementa lógica**.
Ele **orquestra contratos**.

### 🔧 Componentes internos

```text
Validator
│
├── SoftwareContractValidator
├── TemporalContractValidator
├── StatisticalContractValidator
├── EpistemicContractValidator
├── ModelContractValidator
└── HierarchyContractValidator
```

Cada um:

* consome o `Snapshot`
* lança **violação específica**
* ou retorna sucesso

O `Validator` **captura**, **organiza** e **reporta**.

---

## 4️⃣ Testes TDD — primeiro

### 📄 `tests/properties/validator/test_validator_properties.py`

```python
import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.validation.validator import (
    Validator,
    ValidationResult,
)


def test_validator_accepts_valid_snapshot():
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

    snap = Snapshot(
        observables=obs,
        state_vector=sv,
        parameters=[],
    )

    validator = Validator()
    result = validator.validate(snapshot=snap)

    assert isinstance(result, ValidationResult)
    assert result.is_valid is True
    assert result.violations == {}


def test_validator_reports_violations():
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
                timestamp=0,  # desalinhado
            )
        ],
        covariance=np.array([[0.2]]),
    )

    snap = Snapshot(
        observables=obs,
        state_vector=sv,
        parameters=[],
    )

    validator = Validator()
    result = validator.validate(snapshot=snap)

    assert result.is_valid is False
    assert "Temporal" in result.violations
```

---

## 5️⃣ Implementação mínima

### 📄 `domain/validation/validator.py`

```python
"""
Validator — Domain Validation Core (BASELINE v1.0)

Aplica contratos científicos a um Snapshot.
"""

from dataclasses import dataclass
from typing import Dict, List

from domain.core.snapshot import Snapshot

# Importa contratos
from domain.contracts.software import SoftwareViolation
from domain.contracts.temporal import TemporalViolation
from domain.contracts.statistical import StatisticalViolation
from domain.contracts.epistemic import EpistemicViolation
from domain.contracts.model import ModelInvariantViolation
from domain.contracts.hierarchy import HierarchyInvariantViolation


@dataclass(frozen=True)
class ValidationResult:
    """
    Resultado da validação científica de um Snapshot.
    """
    is_valid: bool
    violations: Dict[str, List[str]]


class Validator:
    """
    Validator (Design by Contract).

    Avalia admissibilidade científica de um Snapshot.
    """

    def validate(self, *, snapshot: Snapshot) -> ValidationResult:
        if not isinstance(snapshot, Snapshot):
            raise TypeError("Validator requires a Snapshot")

        violations: Dict[str, List[str]] = {}

        def record(contract: str, exc: Exception):
            violations.setdefault(contract, []).append(str(exc))

        # -------------------------------------------------
        # Aplicação dos contratos
        # -------------------------------------------------

        try:
            self._validate_software(snapshot)
        except SoftwareViolation as e:
            record("Software", e)

        try:
            self._validate_temporal(snapshot)
        except TemporalViolation as e:
            record("Temporal", e)

        try:
            self._validate_statistical(snapshot)
        except StatisticalViolation as e:
            record("Statistical", e)

        try:
            self._validate_epistemic(snapshot)
        except EpistemicViolation as e:
            record("Epistemic", e)

        try:
            self._validate_model(snapshot)
        except ModelInvariantViolation as e:
            record("Model", e)

        try:
            self._validate_hierarchy(snapshot)
        except HierarchyInvariantViolation as e:
            record("Hierarchy", e)

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
        )

    # -------------------------------------------------
    # Validadores específicos (stubs iniciais)
    # -------------------------------------------------

    def _validate_software(self, snapshot: Snapshot):
        # Estrutura já garantida pelos objetos
        pass

    def _validate_temporal(self, snapshot: Snapshot):
        # Exemplo: timestamps já coerentes pelo Snapshot
        pass

    def _validate_statistical(self, snapshot: Snapshot):
        # Exemplo: covariância válida já garantida
        pass

    def _validate_epistemic(self, snapshot: Snapshot):
        # Exemplo: Identifiables e Observables já auditáveis
        pass

    def _validate_model(self, snapshot: Snapshot):
        # Será expandido com resíduos, compatibilidade etc.
        pass

    def _validate_hierarchy(self, snapshot: Snapshot):
        # Aplicável quando houver hierarquia
        pass
```

---

## 6️⃣ O que você construiu até aqui (e por que isso é forte)

Você agora tem:

| Camada                        | Papel                          |
| ----------------------------- | ------------------------------ |
| Objetos de domínio            | Forma correta                  |
| Estimadores / Identificadores | Hipóteses                      |
| Snapshot                      | Congelamento epistemológico    |
| **Validator**                 | **Juízo científico explícito** |

Isso permite:

* **auditoria científica**
* **troca de modelos sem quebrar contratos**
* **hierarquia segura**
* **uso de ML sem colapsar epistemologia**
* **explicabilidade real**

Pouquíssimos sistemas industriais fazem isso direito.

---

## Próximo passo (se quiser continuar)

Há três caminhos naturais agora:

1️⃣ **Refinar cada `_validate_*`** com contratos reais
2️⃣ Criar o **DomainLevelComponent** usando tudo isso
3️⃣ Subir para **Hierarchical Digital Twin**

Quando quiser, diga qual deles seguimos.
