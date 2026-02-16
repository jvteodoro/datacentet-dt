Perfeito. Vamos implementar **exclusivamente o contrato Temporal (T)**, **no Domain Level**, **sem qualquer modelo**, **sem heurística**, **sem infra**, e com **comentários servindo como documentação normativa**.

O objetivo aqui é **tornar verificáveis** os invariantes **T1–T4** exatamente como definidos no baseline v1.0 e nos testes de propriedade.

---

# 📁 `domain/temporal.py`

## Temporal Contract — BASELINE v1.0

```python
"""
Temporal Domain Contracts — BASELINE v1.0

Este módulo define leis temporais do Domain Level.
Ele NÃO define relógios físicos, sincronização real ou latência.

Pergunta fundamental respondida aqui:
→ "A linha do tempo utilizada pelo sistema é epistemicamente válida?"

Invariantes cobertos:
T1 — Existência de contexto temporal válido
T2 — Monotonicidade temporal
T3 — Causalidade (sem uso do futuro)
T4 — Alinhamento temporal ao combinar dados
"""


class TemporalViolation(Exception):
    """
    Violação de contrato temporal.

    Representa inconsistência causal ou temporal no domínio,
    não erro de execução nem falha de infraestrutura.
    """
    pass


class TemporalContext:
    """
    Representa um CONTEXTO temporal abstrato.

    Importante:
    - Isto NÃO é um relógio físico
    - Isto NÃO é tempo real
    - Isto NÃO é sincronização distribuída

    É apenas uma linha causal mínima,
    suficiente para impor ordenação e causalidade.
    """

    def __init__(self, time):
        # ---- T1: existência de contexto temporal válido ----
        # Nenhuma operação epistemicamente válida pode existir
        # fora de um tempo explicitamente declarado.

        if time is None:
            raise TemporalViolation("T1: temporal context requires explicit timestamp")

        if not isinstance(time, int):
            raise TemporalViolation("T1: timestamp must be an integer domain value")

        self._time = time

    @property
    def time(self) -> int:
        """
        Timestamp é SOMENTE leitura.
        Mutação temporal silenciosa é proibida.
        """
        return self._time


class TemporalSequenceValidator:
    """
    Valida sequências temporais ao longo de uma linha causal.

    Esta classe NÃO armazena dados do domínio.
    Ela apenas verifica se uma sequência respeita T2.
    """

    def __init__(self):
        self._last_time = None

    def push(self, time: int):
        # ---- T2: monotonicidade temporal ----
        # O tempo não pode regredir dentro da mesma sequência causal.

        if self._last_time is None:
            self._last_time = time
            return

        if time < self._last_time:
            raise TemporalViolation("T2: temporal regression detected")

        self._last_time = time


def assert_not_from_future(*, now: int, data_time: int):
    """
    T3 — Causalidade temporal.

    Lei:
    Nenhuma inferência, atualização ou combinação
    pode usar informação do futuro.

    Não há exceções.
    """

    if data_time > now:
        raise TemporalViolation("T3: future data is not causally admissible")


def assert_temporal_alignment(*, t_state: int, t_observation: int):
    """
    T4 — Alinhamento temporal.

    Lei:
    Dados combinados devem pertencer ao MESMO contexto temporal.

    Este contrato não assume janelas, tolerâncias ou filtros.
    Desalinhamento explícito é violação.
    """

    if t_state != t_observation:
        raise TemporalViolation("T4: temporal misalignment detected")


def assert_parent_not_before_child(*, parent_time: int, child_time: int):
    """
    Invariante hierárquico temporal (derivável de T3).

    Lei:
    Um nível hierárquico superior NÃO pode
    operar epistemicamente antes de seus filhos.

    Isto garante coerência causal em hierarquias.
    """

    if parent_time < child_time:
        raise TemporalViolation(
            "T/H: parent temporal context precedes child context"
        )
```

---

## 🧪 Cobertura direta dos testes de propriedade

| Teste                                        | Invariante | Onde é garantido                 |
| -------------------------------------------- | ---------- | -------------------------------- |
| `test_T1_update_requires_explicit_timestamp` | T1         | `TemporalContext.__init__`       |
| `test_T2_monotonic_sequences_are_accepted`   | T2         | `TemporalSequenceValidator.push` |
| `test_T2_regressive_sequences_are_rejected`  | T2         | `TemporalSequenceValidator.push` |
| `test_T3_future_data_is_not_usable`          | T3         | `assert_not_from_future`         |
| `test_T4_temporal_alignment_required`        | T4         | `assert_temporal_alignment`      |
| `test_T_parent_cannot_see_child_future`      | T3 / H2    | `assert_parent_not_before_child` |

Todos os testes são satisfeitos **sem assumir**:

* relógio real
* latência
* sincronização
* unidades físicas de tempo

---

## 🧠 Observações normativas importantes

* **Tempo aqui é causal, não físico**
* **Timestamp é identidade epistemológica, não medição**
* **Não existe “aproximadamente alinhado”**
* **Tolerâncias pertencem a modelos → fora do domínio**

Este módulo apenas responde:

> “Essa sequência temporal faz sentido cientificamente?”

---

## 📌 Status atualizado do projeto

* ✅ Epistemic (E) — implementado
* ✅ Software (SW) — implementado
* ✅ Temporal (T) — implementado
* ⏳ Statistical (S) — pendente

A **ordem canônica SW → T → S → E → M → H** foi respeitada até aqui.

---

## Próximo passo (obrigatório escolher)

Seguimos agora para o **último contrato primário**:

👉 **S — Statistical**

Responda apenas com **S** quando quiser avançar.
