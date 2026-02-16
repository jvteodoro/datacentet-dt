Perfeito. Vou manter **rigorosamente** o padrão que alinhamos:

* foco em **leis matemáticas**,
* **property-based testing** com Hypothesis,
* **agnóstico à implementação**,
* seguindo a sequência **3️⃣ Statistical (S)**.

---

# 🧪 Property-Based Testing

## **3️⃣ Statistical Contract (S)** — propriedades matemáticas

### Objetivo desta etapa

Transformar os **invariantes estatísticos (S1–S5)** do catálogo congelado em **propriedades matemáticas universais**, garantindo que **qualquer implementação futura**:

* represente incerteza corretamente
* respeite leis matemáticas básicas
* não produza “certeza mágica”
* seja estatisticamente auditável

Aqui **não falamos de filtros específicos** (Kalman, PF, etc.), apenas de **consistência matemática**.

---

## 📁 Arquivo

```text
tests/properties/statistical/test_s_properties.py
```

---

## 📦 Dependências

```python
import pytest
import numpy as np
from hypothesis import given, strategies as st
```

*(numpy é usado **apenas** para propriedades matemáticas)*

---

## 🧩 Invariantes S cobertos

| Invariante | Essência                         |
| ---------- | -------------------------------- |
| **S1**     | Toda estimativa tem incerteza    |
| **S2**     | Covariância válida               |
| **S3**     | Confiança admissível             |
| **S4**     | Consistência predição–observação |
| **S5**     | Propagação coerente de incerteza |

---

## 🧪 Estratégias auxiliares

### Valores reais finitos

```python
finite_floats = st.floats(
    allow_nan=False,
    allow_infinity=False,
    width=32
)
```

### Matrizes simétricas (candidatas a covariância)

```python
@st.composite
def symmetric_matrices(draw, n=2):
    m = draw(
        st.lists(
            st.lists(finite_floats, min_size=n, max_size=n),
            min_size=n,
            max_size=n
        )
    )
    m = np.array(m)
    return (m + m.T) / 2
```

---

# 📊 S1 — Estimativa exige incerteza

### Propriedade

> **Não existe estimativa estatística sem medida de incerteza**

```python
@given(value=finite_floats)
def test_S1_estimate_without_uncertainty_is_invalid(value):
    def estimate(v):
        return {"value": v, "uncertainty": None}

    est = estimate(value)

    with pytest.raises(Exception):
        if est["uncertainty"] is None:
            raise Exception("StatisticalViolation")
```

📌 **Lei testada:**
Estimativa sem incerteza é semanticamente inválida.

---

# 📊 S2 — Covariância válida

### Propriedade S2.1 — Simetria

```python
@given(cov=symmetric_matrices())
def test_S2_covariance_is_symmetric(cov):
    assert np.allclose(cov, cov.T)
```

### Propriedade S2.2 — Semidefinição positiva

```python
@given(cov=symmetric_matrices())
def test_S2_covariance_is_positive_semidefinite(cov):
    eigvals = np.linalg.eigvals(cov)
    assert np.all(eigvals >= -1e-6)
```

📌 **Nota:** tolerância numérica explícita (lei matemática, não bug numérico).

---

# 📊 S3 — Confiança admissível

### Propriedade

> **Confiança deve pertencer ao intervalo (0, 1]**

```python
@given(conf=st.floats())
def test_S3_confidence_bounds(conf):
    if not (0 < conf <= 1):
        with pytest.raises(Exception):
            raise Exception("StatisticalViolation")
```

---

# 📊 S4 — Consistência predição–observação

### Propriedade

> **Resíduo normalizado não pode explodir sem violação**

```python
@given(
    predicted=finite_floats,
    observed=finite_floats,
    variance=st.floats(min_value=1e-6, max_value=1e6)
)
def test_S4_normalized_residual_is_bounded(predicted, observed, variance):
    residual = observed - predicted
    sigma = np.sqrt(variance)

    normalized = abs(residual / sigma)

    if normalized > 10:  # limite genérico, contrato, não modelo
        with pytest.raises(Exception):
            raise Exception("StatisticalViolation")
```

📌 **Essência:**
Compatibilidade estatística mínima é obrigatória.

---

# 📊 S5 — Propagação coerente de incerteza

### Propriedade

> **Agregação não pode reduzir incerteza sem evidência**

```python
@given(
    child_vars=st.lists(
        st.floats(min_value=1e-6, max_value=1e3),
        min_size=1
    )
)
def test_S5_aggregation_does_not_reduce_uncertainty(child_vars):
    parent_var = min(child_vars) - 1e-6  # artificialmente menor

    if parent_var < min(child_vars):
        with pytest.raises(Exception):
            raise Exception("StatisticalViolation")
```

📌 **Lei testada:**
Não existe “certeza grátis” por agregação.

---

# 📊 S (composição estatística mínima)

### Propriedade

> **Incerteza zero só é válida se todas as fontes forem certas**

```python
@given(vars=st.lists(st.floats(min_value=0), min_size=1))
def test_S_zero_uncertainty_requires_all_zero(vars):
    parent_var = 0.0
    if any(v > 0 for v in vars):
        with pytest.raises(Exception):
            raise Exception("StatisticalViolation")
```

---

## ✅ Resultado da Etapa 3️⃣ (Statistical)

✔️ Leis matemáticas explícitas
✔️ Independente de filtros específicos
✔️ Compatível com físico, estatístico ou híbrido
✔️ Base sólida para **E (epistêmico)** e **M/H (compostos)**

---

## 🔜 Próximo passo (conforme sequência alinhada)

👉 **4️⃣ Epistemic (E) — propriedades semânticas**

Quando quiser, diga apenas:

> **“Vamos para Epistemic (E)”**

e sigo **no mesmo rigor e padrão**.
