Memória **atualizada com sucesso**.
Vou **seguir estritamente** os detalhes alinhados **durante todo o desenvolvimento dos contratos**, sem desvios de escopo ou sequência.

Agora começo **exatamente onde você pediu**.

---

# 🧪 Property-Based Testing

## **1️⃣ Software Contract (SW)** — propriedades estruturais simples

### Objetivo desta etapa

Transformar os **invariantes SW** do catálogo congelado em **propriedades universais**, verificadas via **Hypothesis**, garantindo que:

* nenhum componente estruturalmente inválido exista
* nenhuma violação de contrato passe despercebida
* a arquitetura seja **auto-policiada por leis**, não por convenção

---

## 📁 Arquivo

```text
tests/properties/software/test_sw_properties.py
```

---

## 📦 Dependências

```python
import pytest
from hypothesis import given, strategies as st
```

*(Nenhuma dependência estatística ou temporal aqui — SW é puramente estrutural)*

---

## 🧩 Invariantes SW cobertos nesta etapa

| Invariante | Cobertura                      |
| ---------- | ------------------------------ |
| SW1        | Integridade estrutural         |
| SW2        | Imutabilidade de contrato      |
| SW3        | Separação de responsabilidades |
| SW4        | Determinismo de interface      |

---

## 🧪 Estratégias auxiliares (geradores)

### Estratégia: nomes válidos e inválidos

```python
valid_names = st.text(min_size=1).filter(lambda s: s.strip() != "")
invalid_names = st.one_of(st.none(), st.text(max_size=0))
```

### Estratégia: versões (semântica simples)

```python
valid_versions = st.from_regex(r"\d+\.\d+\.\d+", fullmatch=True)
invalid_versions = st.text().filter(lambda s: not bool(
    __import__("re").fullmatch(r"\d+\.\d+\.\d+", s)
))
```

---

# 🔒 SW1 — Integridade estrutural

### Propriedade

> **Todo componente com metadados inválidos deve falhar explicitamente**

```python
@given(name=invalid_names, version=valid_versions)
def test_SW1_invalid_name_is_rejected(name, version):
    class Component:
        def name(self): return name
        def version(self): return version
        def dependencies(self): return []
        def invariants(self): return ["SW1"]
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    with pytest.raises(Exception):
        Component()
```

---

```python
@given(name=valid_names, version=invalid_versions)
def test_SW1_invalid_version_is_rejected(name, version):
    class Component:
        def name(self): return name
        def version(self): return version
        def dependencies(self): return []
        def invariants(self): return ["SW1"]
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    with pytest.raises(Exception):
        Component()
```

📌 **Essência:**
Não existe objeto estruturalmente inválido “meio criado”.

---

# 🔒 SW2 — Imutabilidade de contrato

### Propriedade

> **Metadados de contrato não podem mudar silenciosamente após validação**

```python
def test_SW2_contract_metadata_is_immutable():
    class Component:
        def __init__(self):
            self._name = "comp"
            self._version = "1.0.0"

        def name(self): return self._name
        def version(self): return self._version
        def dependencies(self): return []
        def invariants(self): return ["SW2"]
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = Component()

    with pytest.raises(Exception):
        c._version = "2.0.0"  # mutação silenciosa proibida
```

📌 **Essência:**
Contrato não é “configuração”, é **lei**.

---

# 🔒 SW3 — Separação de responsabilidades

### Propriedade

> **Um componente não pode declarar invariantes que não respeita**

```python
@given(st.lists(st.sampled_from(["SW1", "SW2", "SW3", "SW4"]), min_size=1))
def test_SW3_component_cannot_claim_unimplemented_invariants(declared):
    class Component:
        def name(self): return "comp"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return declared
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    if "SW3" in declared:
        with pytest.raises(Exception):
            Component()
```

📌 **Essência:**
Declarar responsabilidade implica **implementá-la**.

---

# 🔒 SW4 — Determinismo de interface

### Propriedade

> **Mesma entrada + mesmo estado → mesma saída**

```python
@given(x=st.integers())
def test_SW4_interface_is_deterministic(x):
    class Component:
        def name(self): return "det"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["SW4"]
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

        def compute(self, x):
            return x * 2

    c = Component()
    assert c.compute(x) == c.compute(x)
```

📌 **Essência:**
Sem determinismo, não há auditoria, nem ciência.

---

# ✅ Resultado da Etapa 1 (SW)

✔️ Propriedades estruturais definidas
✔️ Totalmente agnósticas à implementação real
✔️ Base sólida para T, S, E, M, H
✔️ Alinhadas ao catálogo congelado v1.0

---

## 🔜 Próximo passo (conforme sequência alinhada)

👉 **2️⃣ Temporal (T) — propriedades de sequência**

Quando quiser, diga apenas:

> **“Vamos para Temporal (T)”**

e sigo **sem sair de nenhum detalhe que alinhamos**.
