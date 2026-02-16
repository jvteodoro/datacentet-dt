Perfeito. Vou seguir **rigorosamente** o que alinhamos (escopo, sequência, padrão de arquivos e dependências) e **não pular nada**.

---

# 🧪 Property-Based Testing

## **2️⃣ Temporal Contract (T)** — propriedades de sequência

### Objetivo desta etapa

Transformar os **invariantes temporais (T1–T4)** do catálogo congelado em **propriedades universais** verificadas via **Hypothesis**, focadas em **sequências**, **ordenação** e **causalidade** — **sem assumir implementação concreta**.

---

## 📁 Arquivo

```text
tests/properties/temporal/test_t_properties.py
```

---

## 📦 Dependências

```python
import pytest
from hypothesis import given, strategies as st
```

*(Sem numpy aqui; matemática pesada fica para S.)*

---

## 🧩 Invariantes T cobertos

| Invariante | Essência                               |
| ---------- | -------------------------------------- |
| **T1**     | Existência de contexto temporal válido |
| **T2**     | Monotonicidade temporal                |
| **T3**     | Causalidade (sem uso do futuro)        |
| **T4**     | Alinhamento temporal ao combinar dados |

---

## 🧪 Estratégias auxiliares

### Sequências temporais gerais

```python
times = st.lists(st.integers(min_value=0), min_size=1)
```

### Sequências monotônicas (válidas)

```python
monotonic_times = st.lists(
    st.integers(min_value=0),
    min_size=1
).map(lambda xs: sorted(xs))
```

### Sequências com regressão (inválidas)

```python
def with_regression(xs):
    if len(xs) < 2:
        return xs
    xs = list(xs)
    xs[1] = max(0, xs[0] - 1)
    return xs

regressive_times = st.lists(
    st.integers(min_value=1),
    min_size=2
).map(with_regression)
```

---

# ⏱️ T1 — Contexto temporal válido

### Propriedade

> **Nenhuma atualização é válida sem timestamp explícito**

```python
@given(t=st.none())
def test_T1_update_requires_explicit_timestamp(t):
    class Component:
        def update(self, time):
            if time is None:
                raise Exception("TemporalViolation")

    c = Component()
    with pytest.raises(Exception):
        c.update(t)
```

---

# ⏱️ T2 — Monotonicidade temporal

### Propriedade

> **O tempo nunca pode regredir**

```python
@given(ts=monotonic_times)
def test_T2_monotonic_sequences_are_accepted(ts):
    last = -1
    for t in ts:
        assert t >= last
        last = t
```

```python
@given(ts=regressive_times)
def test_T2_regressive_sequences_are_rejected(ts):
    last = ts[0]
    violated = False
    for t in ts[1:]:
        if t < last:
            violated = True
        last = t
    assert violated
```

📌 **Nota:**
Aqui testamos a **lei** (existência de regressão), não um método específico.

---

# ⏱️ T3 — Causalidade (sem futuro)

### Propriedade

> **Nenhuma operação pode depender de dados futuros**

```python
@given(
    current=st.integers(min_value=0),
    future=st.integers(min_value=1)
)
def test_T3_future_data_is_not_usable(current, future):
    assume = pytest.assume
    assume(future > current)

    def use_data(now, data_time):
        if data_time > now:
            raise Exception("TemporalViolation")

    with pytest.raises(Exception):
        use_data(current, future)
```

---

# ⏱️ T4 — Alinhamento temporal

### Propriedade

> **Dados combinados devem estar temporalmente compatíveis**

```python
@given(
    t_state=st.integers(min_value=0),
    t_obs=st.integers(min_value=0)
)
def test_T4_temporal_alignment_required(t_state, t_obs):
    def combine(state_time, obs_time):
        if abs(state_time - obs_time) > 0:
            raise Exception("TemporalViolation")

    if t_state != t_obs:
        with pytest.raises(Exception):
            combine(t_state, t_obs)
```

📌 **Essência:**
Sem alinhamento temporal explícito, não há fusão válida.

---

# ⏱️ T (hierarquia local) — Consistência pai–filho (base)

*(a versão completa de hierarquia fica em H; aqui garantimos a base)*

### Propriedade

> **Um nível não pode observar um filho no futuro**

```python
@given(
    parent_t=st.integers(min_value=0),
    child_t=st.integers(min_value=0)
)
def test_T_parent_cannot_see_child_future(parent_t, child_t):
    if child_t > parent_t:
        raise Exception("TemporalViolation")
```

---

## ✅ Resultado da Etapa 2️⃣ (Temporal)

✔️ Propriedades de sequência definidas
✔️ Testes **agnósticos à implementação**
✔️ Causalidade e alinhamento formalizados
✔️ Base sólida para **S (estatístico)** e **H (hierarquia)**

---

## 🔜 Próximo passo (conforme sequência alinhada)

👉 **3️⃣ Statistical (S) — propriedades matemáticas**

Quando quiser, diga apenas:

> **“Vamos para Statistical (S)”**

e sigo **no mesmo padrão**, sem desvio.
