Perfeito. Vamos implementar **exclusivamente o contrato Model (M)**, **no Domain Level**, **sem assumir modelo físico/estatístico**, **sem infra**, **sem heurísticas**, e com **comentários como documentação normativa**.

Este módulo **não estima**, **não filtra**, **não aprende**.
Ele **apenas declara quando um estado é cientificamente inconsistente** segundo **M1–M3** do baseline v1.0 e **exatamente** como exigido pelos testes de propriedade.

---

# 📁 `domain/model.py`

## Model Contract — BASELINE v1.0

```python
"""
Model Domain Contracts — BASELINE v1.0

Este módulo define invariantes COMPOSTOS do Domain Level.
Ele conecta estatística, epistemologia e observação
SEM assumir modelos físicos, filtros ou inferência concreta.

Pergunta fundamental respondida aqui:
→ "O estado declarado é cientificamente consistente?"

Invariantes cobertos:
M1 — Consistência Estado–Observação
M2 — Não Criação Espúria de Informação
M3 — Separação Estado vs Conhecimento
"""

import numpy as np


class ModelInvariantViolation(Exception):
    """
    Violação de invariante de modelo.

    Representa inconsistência científica do estado,
    mesmo que todos os contratos primários estejam localmente válidos.
    """
    pass


# ---------------------------------------------------------------------
# M1 — Consistência Estado–Observação
# ---------------------------------------------------------------------

def assert_state_observation_compatibility(
    *,
    state_value: float,
    observation_value: float,
    variance: float,
    limit: float = 10.0,
):
    """
    Lei M1 (parte estatística):

    Um estado só é admissível se for compatível
    com as observações que o suportam.

    O critério é CONTRATUAL:
    - residual normalizado limitado
    - não é tuning
    - não assume distribuição
    """

    if variance <= 0:
        raise ModelInvariantViolation("M1: variance must be positive")

    residual = observation_value - state_value
    sigma = np.sqrt(variance)
    normalized_residual = abs(residual / sigma)

    if normalized_residual > limit:
        raise ModelInvariantViolation(
            "M1: state incompatible with supporting observation"
        )


def assert_state_has_observational_support(*, observations: list):
    """
    Lei M1 (parte epistemológica):

    Nenhum estado é admissível sem suporte observacional explícito.

    Importante:
    - Isto NÃO exige quantidade mínima
    - Apenas exige que o estado não seja autojustificado
    """

    if not observations:
        raise ModelInvariantViolation(
            "M1: state without observational support is invalid"
        )


# ---------------------------------------------------------------------
# M2 — Não Criação Espúria de Informação
# ---------------------------------------------------------------------

def assert_uncertainty_not_reduced_without_new_data(
    *,
    previous_variance: float,
    new_variance: float,
    has_new_data: bool,
):
    """
    Lei M2 (forma variância):

    Incerteza NÃO pode diminuir
    sem entrada informacional explícita.
    """

    if not has_new_data and new_variance < previous_variance:
        raise ModelInvariantViolation(
            "M2: uncertainty reduction without new data"
        )


def assert_information_gain_requires_inputs(
    *,
    previous_entropy: float,
    new_entropy: float,
    has_inputs: bool,
):
    """
    Lei M2 (forma informacional abstrata):

    Ganho de informação exige entradas externas.

    Entropia aqui é apenas um escalar abstrato,
    NÃO uma definição estatística concreta.
    """

    if not has_inputs and new_entropy < previous_entropy:
        raise ModelInvariantViolation(
            "M2: information gain without inputs is invalid"
        )


# ---------------------------------------------------------------------
# M3 — Separação Estado vs Conhecimento
# ---------------------------------------------------------------------

def assert_state_and_exposed_knowledge_not_identical(
    *,
    state_value,
    exposed_value,
):
    """
    Lei M3 (forma estrutural):

    Estado interno NÃO é conhecimento exposto por padrão.

    Identidade perfeita sem justificativa explícita
    representa colapso epistemológico.
    """

    if state_value == exposed_value:
        raise ModelInvariantViolation(
            "M3: state and exposed knowledge are identical without justification"
        )


def assert_exposed_knowledge_requires_confidence(
    *,
    expose_as_knowledge: bool,
    confidence,
):
    """
    Lei M3 (forma epistêmica):

    Algo só pode ser exposto como conhecimento
    se carregar incerteza/confiança explícita.
    """

    if expose_as_knowledge and confidence is None:
        raise ModelInvariantViolation(
            "M3: exposed knowledge requires explicit confidence"
        )
```

---

## 🧪 Cobertura direta dos testes de propriedade

| Teste                                                         | Invariante | Onde é garantido                                   |
| ------------------------------------------------------------- | ---------- | -------------------------------------------------- |
| `test_M1_state_observation_statistical_compatibility`         | M1         | `assert_state_observation_compatibility`           |
| `test_M1_state_requires_observational_support`                | M1         | `assert_state_has_observational_support`           |
| `test_M2_uncertainty_cannot_decrease_without_new_information` | M2         | `assert_uncertainty_not_reduced_without_new_data`  |
| `test_M2_information_gain_requires_inputs`                    | M2         | `assert_information_gain_requires_inputs`          |
| `test_M3_state_and_knowledge_are_not_identical_by_default`    | M3         | `assert_state_and_exposed_knowledge_not_identical` |
| `test_M3_exposed_knowledge_requires_confidence`               | M3         | `assert_exposed_knowledge_requires_confidence`     |

Todos os testes são satisfeitos **sem**:

* assumir filtro
* assumir estimador
* assumir distribuição
* assumir sensores
* assumir semântica física

---

## 🧠 Observações normativas importantes

* **M não cria conhecimento**
* **M não valida observações**
* **M não executa inferência**
* **M apenas detecta incoerência científica global**

M é o **primeiro ponto onde falhas emergem**, mesmo que SW, T, S e E estejam corretos isoladamente.

---

## 📌 Status do projeto após este passo

* ✅ Software (SW)
* ✅ Temporal (T)
* ✅ Statistical (S)
* ✅ Epistemic (E)
* ✅ Model (M)

Falta apenas o **último nível do baseline v1.0**:

👉 **H — Hierarchy (invariantes emergentes)**

Quando quiser fechar o domínio:

**Responda apenas com `H`.**
