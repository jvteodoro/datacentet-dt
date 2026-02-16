Perfeito. Vamos fazer **do jeito correto para este projeto**:

* ✅ **somente Domain Level**
* ✅ **somente contratos**
* ✅ **código mínimo, normativo e auditável**
* ✅ **comentários = documentação científica**
* ❌ nenhuma heurística, nenhum modelo, nenhuma infra

Vou começar **APENAS com o contrato Epistêmico (E)**, porque:

* ele é semanticamente central,
* os testes já delimitam exatamente o espaço permitido,
* ele não depende de SW/T/S para existir (apenas para ser usado depois).

Nada dos outros contratos será tocado ainda.

---

# 📁 domain/epistemic.py

## Contrato Epistêmico — BASELINE v1.0

```python
"""
Epistemic Domain Contracts — BASELINE v1.0

Este módulo define exclusivamente leis epistêmicas do domínio.
Ele NÃO implementa inferência, estatística ou lógica física.

Aqui só existe uma pergunta:
→ "Aquilo que está sendo declarado como conhecimento é cientificamente válido?"

Todos os invariantes implementados aqui derivam diretamente de:
E1, E2, E3, E4, E5 (ver catálogo congelado).
"""


class EpistemicViolation(Exception):
    """
    Violação de contrato epistêmico.

    Esta exceção não representa erro de execução,
    mas inconsistência científica no domínio.
    """
    pass


class EpistemicRecord:
    """
    Representa UMA unidade mínima de conhecimento epistêmico.

    Importante:
    - Isto NÃO é um modelo estatístico
    - Isto NÃO é um resultado computacional
    - Isto NÃO é um fato do mundo

    É apenas uma afirmação:
    "Acreditamos que X é verdadeiro, com confiança C, por estes motivos"
    """

    def __init__(
        self,
        *,
        value,
        source: str,
        method: str,
        justification: str,
        confidence: float,
        is_inferred: bool = False,
        is_fact: bool = False,
    ):
        # ---- E1: Integridade epistêmica ----
        # Todo conhecimento deve responder explicitamente:
        # "De onde veio?", "Como foi obtido?", "Por quê acreditamos nisso?"

        if not source or not isinstance(source, str) or not source.strip():
            raise EpistemicViolation("E1: missing or invalid source")

        if not method or not isinstance(method, str) or not method.strip():
            raise EpistemicViolation("E1: missing or invalid method")

        if not justification or not isinstance(justification, str) or not justification.strip():
            raise EpistemicViolation("E1: missing or invalid justification")

        # ---- E2: Incerteza epistêmica explícita ----
        # Confiança NÃO é verdade.
        # Confiança é um limite epistemológico explícito.

        if confidence is None or not (0 < confidence <= 1):
            raise EpistemicViolation("E2: confidence must be in (0, 1]")

        # ---- E3: Separação conhecimento vs inferência ----
        # Um registro NÃO pode ser simultaneamente:
        # - inferido
        # - tratado como fato estabilizado

        if is_inferred and is_fact:
            raise EpistemicViolation(
                "E3: inference and fact cannot be true simultaneously"
            )

        # Armazenamento é permitido SOMENTE após validação epistêmica
        self._value = value
        self._source = source
        self._method = method
        self._justification = justification
        self._confidence = confidence
        self._is_inferred = is_inferred
        self._is_fact = is_fact

    # ---- Propriedades somente leitura ----
    # Conhecimento NÃO pode ser mutado silenciosamente

    @property
    def value(self):
        return self._value

    @property
    def source(self):
        return self._source

    @property
    def method(self):
        return self._method

    @property
    def justification(self):
        return self._justification

    @property
    def confidence(self):
        return self._confidence

    @property
    def is_inferred(self):
        return self._is_inferred

    @property
    def is_fact(self):
        return self._is_fact


def validate_epistemic_composition(
    *,
    parent_confidence: float,
    child_confidences: list[float],
):
    """
    E4 — Composição epistêmica segura.

    Lei:
    Conhecimento composto NÃO pode ser mais confiável
    do que sua fonte menos confiável.

    Isto NÃO assume estatística.
    É apenas uma lei de prudência epistemológica.
    """

    if not child_confidences:
        raise EpistemicViolation("E4: composition requires children")

    if parent_confidence > min(child_confidences):
        raise EpistemicViolation(
            "E4: parent confidence cannot exceed weakest child confidence"
        )


def audit_epistemic_record(record: EpistemicRecord):
    """
    E5 — Auditabilidade científica.

    Auditoria significa:
    - Conseguimos responder "por quê?"
    - Conseguimos rastrear a origem
    - Conseguimos explicar o método

    NÃO significa reproduzir cálculo.
    """

    if not all([
        record.source,
        record.method,
        record.justification
    ]):
        raise EpistemicViolation("E5: record is not auditable")
```

---

## ✅ Cobertura explícita dos testes

| Teste                     | Invariante | Onde está coberto                |
| ------------------------- | ---------- | -------------------------------- |
| E1 missing source         | E1         | `__init__`                       |
| E1 missing method         | E1         | `__init__`                       |
| E1 missing justification  | E1         | `__init__`                       |
| E2 invalid confidence     | E2         | `__init__`                       |
| E3 fact + inference       | E3         | `__init__`                       |
| E4 confidence composition | E4         | `validate_epistemic_composition` |
| E5 auditability           | E5         | `audit_epistemic_record`         |

Nenhum teste exige:

* modelos
* estatística
* infra
* IO
* estado global

✔️ 100% aderente ao **baseline v1.0**

---

## 🔒 Observações importantes (domínio)

* **Confidence não é probabilidade**
* **EpistemicRecord não é estado**
* **EpistemicRecord não é observação**
* **Nada aqui “calcula” nada**

Este módulo **só diz quando algo é epistemicamente inválido**.

---

## Próximo passo (obrigatório escolher)

Agora seguimos **exatamente a ordem correta do domínio**.

Qual contrato você quer implementar a seguir?

**1️⃣ Software (SW)**
**2️⃣ Temporal (T)**
**3️⃣ Statistical (S)**

Responda apenas com **SW**, **T** ou **S**.
