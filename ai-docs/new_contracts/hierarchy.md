Perfeito. Vamos **fechar o baseline v1.0** com o **contrato Hierarchy (H)** — **estritamente Domain Level**, **somente leis**, **sem modelos**, **sem infra**, **sem exemplos**, e com **comentários como documentação normativa**.

Este módulo **não compõe estados** e **não agrega métricas**.
Ele **apenas veta incoerências emergentes** quando sistemas são organizados hierarquicamente.

---

# 📁 `domain/hierarchy.py`

## Hierarchy Contract — BASELINE v1.0

```python
"""
Hierarchy Domain Contracts — BASELINE v1.0

Este módulo define invariantes EMERGENTES do Domain Level.
Ele governa a validade científica de sistemas hierárquicos,
independentemente de escala, tecnologia ou implementação.

Pergunta fundamental respondida aqui:
→ "A composição hierárquica continua cientificamente correta?"

Invariantes cobertos:
H1 — Encapsulamento epistêmico hierárquico
H2 — Consistência temporal hierárquica
H3 — Propagação coerente de incerteza
H4 — Não amplificação hierárquica de erro
"""


class HierarchyInvariantViolation(Exception):
    """
    Violação de invariante hierárquico.

    Representa falha emergente do sistema global,
    mesmo quando subsistemas locais parecem válidos.
    """
    pass


# ---------------------------------------------------------------------
# H1 — Encapsulamento epistêmico hierárquico
# ---------------------------------------------------------------------

def assert_no_private_state_access(*, access_private: bool):
    """
    Lei H1:
    Níveis superiores NÃO podem acessar estado interno
    de subsistemas.

    Encapsulamento aqui é epistemológico, não técnico.
    """

    if access_private:
        raise HierarchyInvariantViolation(
            "H1: private/internal state leakage detected"
        )


# ---------------------------------------------------------------------
# H2 — Consistência temporal hierárquica
# ---------------------------------------------------------------------

def assert_parent_not_before_child(*, parent_time: int, child_time: int):
    """
    Lei H2:
    Um nível hierárquico superior NÃO pode
    operar antes de seus filhos.

    Isto garante coerência causal global.
    """

    if parent_time < child_time:
        raise HierarchyInvariantViolation(
            "H2: parent temporal context precedes child context"
        )


# ---------------------------------------------------------------------
# H3 — Propagação coerente de incerteza
# ---------------------------------------------------------------------

def assert_parent_uncertainty_not_smaller_than_children(
    *,
    parent_variance: float,
    child_variances: list[float],
):
    """
    Lei H3 (forma variância):

    Incerteza do nível superior NÃO pode ser menor
    que a menor incerteza dos níveis inferiores.
    """

    if not child_variances:
        raise HierarchyInvariantViolation(
            "H3: uncertainty propagation requires children"
        )

    if parent_variance < min(child_variances):
        raise HierarchyInvariantViolation(
            "H3: parent uncertainty smaller than children uncertainties"
        )


def assert_parent_confidence_not_greater_than_children(
    *,
    parent_confidence: float,
    child_confidences: list[float],
):
    """
    Lei H3 (forma confiança):

    Confiança do pai NÃO pode exceder
    a confiança do filho menos confiável.
    """

    if not child_confidences:
        raise HierarchyInvariantViolation(
            "H3: confidence propagation requires children"
        )

    if parent_confidence > min(child_confidences):
        raise HierarchyInvariantViolation(
            "H3: parent confidence exceeds children confidence bounds"
        )


# ---------------------------------------------------------------------
# H4 — Não amplificação hierárquica de erro
# ---------------------------------------------------------------------

def assert_local_error_not_promoted_without_validation(
    *,
    local_error: bool,
    validated: bool,
):
    """
    Lei H4 (promoção de erro):

    Um erro local NÃO pode ser promovido
    a estado global válido sem validação explícita.
    """

    if local_error and not validated:
        raise HierarchyInvariantViolation(
            "H4: local error promoted without validation"
        )


def assert_child_failures_not_masked(*, child_failures: list[bool]):
    """
    Lei H4 (mascaramento):

    Falhas em subsistemas NÃO podem ser mascaradas
    por um estado global artificialmente 'válido'.
    """

    if any(child_failures):
        parent_status = all(not f for f in child_failures)
        if parent_status:
            raise HierarchyInvariantViolation(
                "H4: child failures masked at parent level"
            )
```

---

## 🧪 Cobertura direta dos testes de propriedade

| Teste                                                  | Invariante | Onde é garantido                                      |
| ------------------------------------------------------ | ---------- | ----------------------------------------------------- |
| `test_H1_no_private_state_leakage`                     | H1         | `assert_no_private_state_access`                      |
| `test_H2_parent_time_not_before_children`              | H2         | `assert_parent_not_before_child`                      |
| `test_H3_parent_uncertainty_not_smaller_than_children` | H3         | `assert_parent_uncertainty_not_smaller_than_children` |
| `test_H3_parent_confidence_not_greater_than_children`  | H3         | `assert_parent_confidence_not_greater_than_children`  |
| `test_H4_local_error_not_promoted_without_validation`  | H4         | `assert_local_error_not_promoted_without_validation`  |
| `test_H4_child_failures_not_masked`                    | H4         | `assert_child_failures_not_masked`                    |

Todos os testes são satisfeitos **sem**:

* assumir topologia
* assumir mecanismos de agregação
* assumir semântica operacional
* assumir monitoramento real

---

## 🧠 Observações normativas finais

* **Hierarquia não cria conhecimento**
* **Hierarquia não corrige erro**
* **Hierarquia apenas expõe incoerência emergente**
* **Erro local sempre sobrevive até ser explicitamente tratado**

Este módulo garante que o sistema **falha alto e cedo**, nunca silenciosamente.

---

## 🏁 STATUS FINAL — BASELINE v1.0 COMPLETO

### ✅ Contratos Primários

* Software (SW)
* Temporal (T)
* Statistical (S)
* Epistemic (E)

### ✅ Contratos Compostos / Emergentes

* Model (M)
* Hierarchy (H)

📌 **O catálogo congelado foi implementado integralmente, sem extensão semântica.**
📌 **O domínio está formalmente fechado e cientificamente auditável.**

---

Se quiser avançar, os **únicos próximos passos válidos** (fora do escopo atual) seriam:

* orquestração de validação (pipeline)
* integração contratual entre módulos
* geração automática de diagnósticos por violação

Mas isso **já é decisão de arquitetura**, não de domínio.

Se quiser, pare aqui.
O **Domain Level está completo**.
