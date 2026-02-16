Perfeito. Vamos implementar **exclusivamente o contrato Statistical (S)**, **no Domain Level**, **sem assumir modelo estatístico**, **sem inferência**, **sem física**, **sem infra**, e com **comentários servindo como documentação normativa**.

Este módulo **não calcula estimativas**.
Ele **apenas declara quando algo é estatisticamente inválido no domínio**.

---

# 📁 `domain/statistical.py`

## Statistical Contract — BASELINE v1.0

```python
"""
Statistical Domain Contracts — BASELINE v1.0

Este módulo define leis estatísticas abstratas do Domain Level.
Ele NÃO assume distribuições, filtros, ruído, sensores ou inferência.

Pergunta fundamental respondida aqui:
→ "A incerteza declarada é matematicamente e cientificamente admissível?"

Invariantes cobertos:
S1 — Toda estimativa tem incerteza
S2 — Covariância válida
S3 — Confiança admissível
S4 — Consistência predição–observação
S5 — Propagação coerente de incerteza
"""

import numpy as np


class StatisticalViolation(Exception):
    """
    Violação de contrato estatístico.

    Representa inconsistência matemática ou científica
    na forma como a incerteza é declarada ou combinada.
    """
    pass


# ---------------------------------------------------------------------
# S1 — Toda estimativa tem incerteza
# ---------------------------------------------------------------------

def assert_has_uncertainty(*, uncertainty):
    """
    Lei S1:
    Nenhuma estimativa é válida sem incerteza explícita.

    Importante:
    - Não importa COMO a incerteza é representada
    - Apenas que ela exista explicitamente
    """

    if uncertainty is None:
        raise StatisticalViolation("S1: estimate without uncertainty is invalid")


# ---------------------------------------------------------------------
# S2 — Covariância válida
# ---------------------------------------------------------------------

def assert_valid_covariance(*, cov: np.ndarray):
    """
    Lei S2:
    Uma matriz de covariância válida deve ser:
    - simétrica
    - semidefinida positiva

    Esta é uma lei matemática,
    não um pressuposto de modelo.
    """

    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise StatisticalViolation("S2: covariance must be square")

    # Simetria
    if not np.allclose(cov, cov.T):
        raise StatisticalViolation("S2: covariance matrix must be symmetric")

    # Semidefinitude positiva
    eigvals = np.linalg.eigvals(cov)
    if np.any(eigvals < -1e-6):
        raise StatisticalViolation(
            "S2: covariance matrix must be positive semidefinite"
        )


# ---------------------------------------------------------------------
# S3 — Confiança admissível
# ---------------------------------------------------------------------

def assert_valid_confidence(*, confidence: float):
    """
    Lei S3:
    Confiança NÃO é verdade.
    Confiança é um limite explícito entre (0, 1].

    Fora desse intervalo → inválido no domínio.
    """

    if not (0 < confidence <= 1):
        raise StatisticalViolation("S3: confidence must be in (0, 1]")


# ---------------------------------------------------------------------
# S4 — Consistência predição–observação
# ---------------------------------------------------------------------

def assert_prediction_observation_consistency(
    *,
    predicted: float,
    observed: float,
    variance: float,
    limit: float = 10.0,
):
    """
    Lei S4:
    Predição e observação devem ser estatisticamente compatíveis.

    O critério aqui é CONTRATUAL:
    - residual normalizado limitado
    - NÃO é tuning
    - NÃO é hipótese de distribuição

    Serve apenas para evitar incompatibilidades extremas.
    """

    if variance <= 0:
        raise StatisticalViolation("S4: variance must be positive")

    residual = observed - predicted
    sigma = np.sqrt(variance)
    normalized = abs(residual / sigma)

    if normalized > limit:
        raise StatisticalViolation(
            "S4: prediction and observation are statistically incompatible"
        )


# ---------------------------------------------------------------------
# S5 — Propagação coerente de incerteza
# ---------------------------------------------------------------------

def assert_uncertainty_not_reduced(
    *,
    parent_variance: float,
    child_variances: list[float],
):
    """
    Lei S5:
    Agregação NÃO pode reduzir incerteza sem nova evidência.

    Esta lei é epistemológica, não algorítmica.
    """

    if not child_variances:
        raise StatisticalViolation("S5: aggregation requires children")

    if parent_variance < min(child_variances):
        raise StatisticalViolation(
            "S5: parent uncertainty cannot be smaller than children uncertainties"
        )


def assert_zero_uncertainty_only_if_all_zero(*, parent_variance, child_variances):
    """
    Caso limite explícito:
    Incerteza zero só é admissível se TODAS as fontes
    também tiverem incerteza zero.

    Evita certeza espúria por composição.
    """

    if parent_variance == 0.0 and any(v > 0 for v in child_variances):
        raise StatisticalViolation(
            "S5: zero uncertainty requires all sources to be zero-uncertainty"
        )
```

---

## 🧪 Cobertura direta dos testes de propriedade

| Teste                                             | Invariante | Onde é garantido                            |
| ------------------------------------------------- | ---------- | ------------------------------------------- |
| `test_S1_estimate_without_uncertainty_is_invalid` | S1         | `assert_has_uncertainty`                    |
| `test_S2_covariance_is_symmetric`                 | S2         | `assert_valid_covariance`                   |
| `test_S2_covariance_is_positive_semidefinite`     | S2         | `assert_valid_covariance`                   |
| `test_S3_confidence_bounds`                       | S3         | `assert_valid_confidence`                   |
| `test_S4_normalized_residual_is_bounded`          | S4         | `assert_prediction_observation_consistency` |
| `test_S5_aggregation_does_not_reduce_uncertainty` | S5         | `assert_uncertainty_not_reduced`            |
| `test_S_zero_uncertainty_requires_all_zero`       | S5         | `assert_zero_uncertainty_only_if_all_zero`  |

Todos os testes são satisfeitos **sem assumir**:

* gaussianidade
* independência
* forma funcional
* modelo de ruído
* método de inferência

---

## 🧠 Observações normativas importantes

* **Variância aqui é apenas um portador abstrato de incerteza**
* **Limite 10 é contrato, não estatística**
* **Nada aqui “estima” nada**
* **Este módulo só veta estados estatisticamente inválidos**

---

## 📌 Status final dos contratos primários

* ✅ Software (SW)
* ✅ Temporal (T)
* ✅ Statistical (S)
* ✅ Epistemic (E)

Os **contratos primários do baseline v1.0 estão completos**.

---

## Próximo passo (natural no domínio)

Agora o sistema está pronto para os **invariantes compostos**:

👉 **M — Model**
👉 **H — Hierarchy**

Qual você quer implementar primeiro?
Responda apenas com **M** ou **H**.
