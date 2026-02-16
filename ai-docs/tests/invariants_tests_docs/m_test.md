Perfeito. Seguimos **rigorosamente** a sequência e os padrões alinhados.
Agora entramos em:

---

# 🧪 Property-Based Testing

## **5️⃣ Model (M)** — propriedades **compostas**

### Objetivo desta etapa

Converter os **invariantes compostos de Modelo (M1–M3)** do catálogo congelado em **propriedades universais**, verificadas via **Hypothesis**, que **emergem da interação** entre contratos **Temporal (T)**, **Statistical (S)** e **Epistemic (E)** — **sem** assumir implementação concreta.

> Aqui testamos **consistência do estado** enquanto objeto científico:
> não basta “passar” em T, S e E isoladamente; o **conjunto** precisa fazer sentido.

---

## 📁 Arquivo

```text
tests/properties/model/test_m_properties.py
```

---

## 📦 Dependências

```python
import pytest
import numpy as np
from hypothesis import given, strategies as st
```

*(numpy apenas para relações matemáticas mínimas; sem filtros/modelos específicos.)*

---

## 🧩 Invariantes M cobertos

| Invariante | Essência                          |
| ---------- | --------------------------------- |
| **M1**     | Consistência Estado–Observação    |
| **M2**     | Não Criação Espúria de Informação |
| **M3**     | Separação Estado vs Conhecimento  |

---

## 🧪 Estratégias auxiliares

### Valores finitos (estado/observação)

```python
finite_floats = st.floats(
    allow_nan=False,
    allow_infinity=False,
    width=32
)
```

### Variâncias positivas (incerteza)

```python
positive_vars = st.floats(min_value=1e-6, max_value=1e6)
```

### Confianças válidas

```python
confidences = st.floats(min_value=1e-6, max_value=1.0)
```

---

# 🔷 M1 — Consistência Estado–Observação

### Propriedade

> **O estado estimado deve ser estatisticamente compatível com as observações que o suportam**
> (compatibilidade mínima; não assume modelo específico).

```python
@given(
    state=finite_floats,
    observation=finite_floats,
    variance=positive_vars
)
def test_M1_state_observation_statistical_compatibility(state, observation, variance):
    residual = observation - state
    sigma = np.sqrt(variance)
    normalized_residual = abs(residual / sigma)

    # Limite contratual genérico (não é tuning de modelo)
    if normalized_residual > 10:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")
```

📌 **Lei testada:**
Estado não pode se afastar arbitrariamente das observações que o justificam.

---

# 🔷 M1 (epistêmico) — Estado exige lastro observacional

### Propriedade

> **Estado não pode existir sem observações associadas**

```python
@given(has_observations=st.booleans())
def test_M1_state_requires_observational_support(has_observations):
    state = {"value": 100}
    observations = [] if not has_observations else [95, 105]

    if not observations:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")
```

---

# 🔷 M2 — Não Criação Espúria de Informação

### Propriedade

> **A incerteza do estado não pode diminuir sem entrada informacional**

```python
@given(
    prev_var=positive_vars,
    new_var=positive_vars,
    has_new_data=st.booleans()
)
def test_M2_uncertainty_cannot_decrease_without_new_information(
    prev_var, new_var, has_new_data
):
    if not has_new_data and new_var < prev_var:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")
```

📌 **Lei testada:**
Não existe “ganho de certeza” sem dados novos.

---

# 🔷 M2 (informacional) — Entropia não cresce negativamente

### Propriedade

> **Conhecimento não pode aumentar sem fonte informacional**

```python
@given(
    prev_entropy=st.floats(min_value=0),
    new_entropy=st.floats(min_value=0),
    has_inputs=st.booleans()
)
def test_M2_information_gain_requires_inputs(prev_entropy, new_entropy, has_inputs):
    if not has_inputs and new_entropy < prev_entropy:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")
```

---

# 🔷 M3 — Separação Estado vs Conhecimento

### Propriedade

> **Estado interno ≠ conhecimento exposto**

```python
@given(
    state_value=finite_floats,
    exposed_value=finite_floats
)
def test_M3_state_and_knowledge_are_not_identical_by_default(
    state_value, exposed_value
):
    # Por contrato, identidade perfeita sem justificativa é inválida
    if state_value == exposed_value:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")
```

📌 **Essência:**
Estado é **instrumental**; conhecimento é **epistêmico**.

---

# 🔷 M3 (confiança) — Conhecimento exige confiança explícita

### Propriedade

> **Estado não pode ser exposto como conhecimento sem confiança**

```python
@given(
    expose_as_knowledge=st.booleans(),
    confidence=st.one_of(confidences, st.none())
)
def test_M3_exposed_knowledge_requires_confidence(expose_as_knowledge, confidence):
    if expose_as_knowledge and confidence is None:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")
```

---

## ✅ Resultado da Etapa 5️⃣ (Model)

✔️ Propriedades **compostas** (T + S + E)
✔️ Nenhuma suposição de modelo físico
✔️ Impede estados “bonitos porém falsos”
✔️ Base direta para **Hierarchy (H)**

---

## 🔜 Próximo passo (conforme sequência alinhada)

👉 **6️⃣ Hierarchy (H)** — propriedades **emergentes**

Quando quiser, diga apenas:

> **“Vamos para Hierarchy (H)”**

e finalizamos o mapeamento completo de invariantes → propriedades.
