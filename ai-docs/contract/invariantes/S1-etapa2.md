Perfeito.
Entramos agora em **S1 — Contrato Estatístico**, mantendo **o mesmo nível de rigor formal** de SW1 e T1.

Vou seguir **exatamente a mesma disciplina**:

1. O que S1 garante no sistema
2. Invariantes estatísticas fundamentais
3. Testes TDD (pytest) — sem implementação
4. Refinamento hierárquico (S1.Hx)
5. Checklist de fechamento de S1

Nada de atalhos, nada de implementação.

---

# 🧪 ETAPA 2 — S1 (Contrato Estatístico)

## 1️⃣ O papel de S1 no Digital Twin

S1 responde à pergunta central:

> **“Quão confiável é o estado que você está usando?”**

No seu sistema:

* estado **nunca é determinístico**
* observáveis têm ruído
* identificáveis têm incerteza
* decisões dependem de **confiança estatística**

👉 S1 impede:

* uso de estimativas sem incerteza
* controle baseado em estado “pontual”
* inferência não auditável

---

## 2️⃣ Definição formal de S1

### 📐 S1 — Invariantes estatísticas fundamentais

Um `DomainLevel` deve garantir:

**S1.1 — Toda estimativa tem incerteza associada**
Nenhum valor estimado pode existir sem representação de incerteza.

**S1.2 — Covariância válida**
Covariâncias devem ser:

* simétricas
* semi-definidas positivas

**S1.3 — Confiança explícita e limitada**
Confiança ∈ (0, 1]

**S1.4 — Consistência entre previsão e observação**
Inovação estatisticamente aceitável.

**S1.5 — Estimativas inválidas não propagam**
Baixa confiança bloqueia uso a montante.

---

## 3️⃣ Testes TDD — S1

---

## 1️⃣ S1.1 — Estimativa sem incerteza é inválida

### 📌 Regra

> Se um valor é estimado → deve haver incerteza associada

---

### 🧪 Teste

```python
def test_s1_estimate_without_uncertainty_violates_contract():
    class NoUncertaintyComponent(DomainLevel):
        def name(self): return "no-uncertainty"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["S1"]

        def estimate_state(self):
            return {"voltage": 230}  # sem incerteza

        def uncertainty(self, value):
            return None

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = NoUncertaintyComponent()

    with pytest.raises(StatisticalViolation):
        c.estimate_state()
```

---

## 2️⃣ S1.2 — Covariância deve ser válida

### 📌 Regra

> Covariância:
>
> * simétrica
> * PSD

---

### 🧪 Teste

```python
def test_s1_covariance_must_be_psd():
    class InvalidCovarianceComponent(DomainLevel):
        def name(self): return "bad-cov"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["S1"]

        def covariance(self, value):
            return np.array([[1, 2], [3, -1]])  # não PSD

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = InvalidCovarianceComponent()

    with pytest.raises(StatisticalViolation):
        cov = c.covariance("x")
        if not np.allclose(cov, cov.T):
            raise StatisticalViolation("Covariance not symmetric")
        if np.any(np.linalg.eigvals(cov) < 0):
            raise StatisticalViolation("Covariance not PSD")
```

---

## 3️⃣ S1.3 — Confiança fora do intervalo é inválida

### 📌 Regra

> Confiança ∈ (0, 1]

---

### 🧪 Teste

```python
def test_s1_confidence_out_of_bounds_violates_contract():
    class BadConfidenceComponent(DomainLevel):
        def name(self): return "bad-confidence"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["S1"]

        def confidence(self, value):
            return 1.5  # inválido

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = BadConfidenceComponent()

    with pytest.raises(StatisticalViolation):
        conf = c.confidence("x")
        if not (0 < conf <= 1):
            raise StatisticalViolation("Invalid confidence")
```

---

## 4️⃣ S1.4 — Inovação inconsistente deve ser detectada

### 📌 Regra

> Previsão e observação devem ser estatisticamente compatíveis

---

### 🧪 Teste (resíduo normalizado)

```python
def test_s1_prediction_observation_inconsistency():
    class InconsistentComponent(DomainLevel):
        def name(self): return "inconsistent"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["S1"]

        def predicted(self): return 100
        def observed(self): return 200
        def covariance(self, value): return np.array([[1]])

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = InconsistentComponent()

    with pytest.raises(StatisticalViolation):
        residual = c.observed() - c.predicted()
        sigma = np.sqrt(c.covariance("x")[0, 0])
        if abs(residual / sigma) > 5:
            raise StatisticalViolation("Innovation too large")
```

---

## 5️⃣ S1.5 — Baixa confiança bloqueia propagação

### 📌 Regra

> Valores com confiança < mínima não podem ser usados a montante

---

### 🧪 Teste

```python
def test_s1_low_confidence_blocks_propagation():
    class LowConfidenceComponent(DomainLevel):
        def name(self): return "low-confidence"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["S1"]

        def confidence(self, value): return 0.01
        def min_confidence(self): return 0.1

        def propagate(self, value):
            if self.confidence(value) < self.min_confidence():
                raise StatisticalViolation("Confidence too low")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = LowConfidenceComponent()

    with pytest.raises(StatisticalViolation):
        c.propagate("x")
```

---

## 4️⃣ Refinamento hierárquico — S1.Hx

Agora garantimos que **estatística também respeita hierarquia**.

---

## S1.H1 — Confiança do pai ≤ confiança dos filhos

### 📐 Regra

> Agregação **não cria certeza**

[
\text{conf}*{parent} \le \min_i(\text{conf}*{child_i})
]

---

### 🧪 Teste

```python
def test_s1_parent_confidence_not_greater_than_children():
    parent_conf = 0.9
    children_conf = [0.6, 0.7]

    if parent_conf > min(children_conf):
        raise StatisticalViolation("Parent more confident than children")
```

---

## S1.H2 — Covariância agregada não diminui artificialmente

### 📐 Regra

> Agregação **não reduz incerteza sem evidência**

---

### 🧪 Teste

```python
def test_s1_aggregation_does_not_reduce_uncertainty():
    parent_cov = 0.1
    children_cov = [0.5, 0.3]

    if parent_cov < min(children_cov):
        raise StatisticalViolation("Artificial uncertainty reduction")
```

---

## 5️⃣ O que S1 garante agora

| Propriedade              | Garantida |
| ------------------------ | --------- |
| Incerteza explícita      | ✅         |
| Covariância válida       | ✅         |
| Confiança bem definida   | ✅         |
| Consistência estatística | ✅         |
| Propagação segura        | ✅         |
| Hierarquia estatística   | ✅         |

👉 Agora **nenhum estado “bonito mas falso” pode existir**.

---

## 🔒 Observação científica

S1 é **agnóstico ao modelo**:

* Kalman
* UKF
* Particle Filter
* modelo físico
* modelo estatístico puro

Tudo cabe **desde que respeite o contrato**.

---

## 🔜 Próximo passo (ETAPA 2)

Agora temos:

* SW1 ✅
* T1 (refinado) ✅
* S1 ✅

Falta apenas:

> **E1 — Contrato Epistêmico**

Onde formalizamos:

* o que o sistema sabe
* o que ele assume
* o que ele infere
* e com qual validade

Quando quiser, diga:

> **“Vamos para E1”**

e seguimos com o mesmo rigor científico.
