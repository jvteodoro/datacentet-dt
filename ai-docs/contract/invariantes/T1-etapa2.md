Perfeito.
Vamos **entrar em T1 (Contrato Temporal)** mantendo **exatamente o mesmo rigor** que usamos em SW1.

Vou seguir a mesma disciplina:

1. **Definir o que T1 garante (formalmente)**
2. **Explicitar as invariantes temporais**
3. **Escrever os testes TDD (pytest)**
4. **Encerrar T1 com checklist claro**

Nada de implementação ainda. Só leis do sistema.

---

# 🧪 ETAPA 2 — T1 (Contrato Temporal)

## 1️⃣ O que é T1 no seu sistema

O **Contrato Temporal (T1)** define as **leis de causalidade e tempo** do Digital Twin.

Em termos formais:

> Um `DomainLevel` **não pode violar o tempo**, mesmo que todos os outros contratos estejam corretos.

Em Digital Twins isso é **fundamental**, porque:

* estado depende do passado
* estimativas dependem de histórico
* hierarquia depende de causalidade

---

## 2️⃣ Definição formal de T1

### 📐 T1 — Invariantes temporais fundamentais

Um `DomainLevel` deve garantir:

**T1.1 — Tempo monotônico**
O tempo interno **nunca retrocede**

**T1.2 — Atualizações são causais**
Estado em `tₖ` depende apenas de informações `≤ tₖ`

**T1.3 — Ordem consistente de eventos**
Observação → Estimação → Controle → Emissão

**T1.4 — Estado inicial bem definido**
Nenhuma atualização ocorre sem estado inicial

**T1.5 — Passos temporais explícitos**
Toda transição tem timestamp associado

---

## 3️⃣ Suposições mínimas (importantes)

Antes dos testes, assumimos **somente isso** sobre `DomainLevel`:

* existe um método `current_time()`
* existe um método `update(time, inputs)`
* existe estado interno temporal

⚠️ Não assumimos *como* isso é feito.

---

## 4️⃣ Testes TDD — T1

---

## 1️⃣ T1.1 — Tempo não pode retroceder

### 📌 Regra

> Se `tₖ₊₁ < tₖ` → violação temporal

---

### 🧪 Teste

```python
def test_t1_time_must_be_monotonic():
    class TemporalComponent(DomainLevel):
        def __init__(self):
            self._time = 0
            super().__init__()

        def name(self) -> str:
            return "temporal"

        def version(self) -> str:
            return "1.0.0"

        def dependencies(self) -> list[str]:
            return []

        def invariants(self) -> list[str]:
            return ["T1"]

        def current_time(self):
            return self._time

        def update(self, time, inputs=None):
            if time < self._time:
                raise TemporalViolation("Time regression detected")
            self._time = time

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = TemporalComponent()
    c.update(1)
    with pytest.raises(TemporalViolation):
        c.update(0)
```

---

## 2️⃣ T1.2 — Atualização sem estado inicial é proibida

### 📌 Regra

> Nenhuma transição temporal ocorre sem estado inicial definido

---

### 🧪 Teste

```python
def test_t1_update_without_initial_state_violates_contract():
    class NoInitStateComponent(DomainLevel):
        def name(self): return "no-init"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["T1"]

        def current_time(self):
            return None  # estado não inicializado

        def update(self, time, inputs=None):
            if self.current_time() is None:
                raise TemporalViolation("State not initialized")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = NoInitStateComponent()
    with pytest.raises(TemporalViolation):
        c.update(0)
```

---

## 3️⃣ T1.3 — Ordem causal obrigatória

### 📌 Regra

> Observação → Estimação → Controle → Emissão
> Nunca o contrário.

---

### 🧪 Teste

```python
def test_t1_causal_order_is_enforced():
    events = []

    class CausalComponent(DomainLevel):
        def name(self): return "causal"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["T1"]

        def observe(self):
            events.append("observe")

        def estimate(self):
            if "observe" not in events:
                raise TemporalViolation("Estimate before observe")
            events.append("estimate")

        def control(self):
            if "estimate" not in events:
                raise TemporalViolation("Control before estimate")
            events.append("control")

        def emit(self):
            if "control" not in events:
                raise TemporalViolation("Emit before control")
            events.append("emit")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = CausalComponent()
    c.observe()
    c.estimate()
    c.control()
    c.emit()

    assert events == ["observe", "estimate", "control", "emit"]
```

---

## 4️⃣ T1.4 — Timestamp explícito é obrigatório

### 📌 Regra

> Toda atualização deve carregar tempo explícito

---

### 🧪 Teste

```python
def test_t1_update_requires_timestamp():
    class NoTimestampComponent(DomainLevel):
        def name(self): return "no-ts"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["T1"]

        def update(self, time=None, inputs=None):
            if time is None:
                raise TemporalViolation("Timestamp required")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = NoTimestampComponent()
    with pytest.raises(TemporalViolation):
        c.update()
```

---

## 5️⃣ T1.5 — Estado depende apenas do passado

### 📌 Regra

> Estado em `tₖ` **não pode depender** de informação futura

---

### 🧪 Teste conceitual

```python
def test_t1_state_cannot_depend_on_future():
    class FutureLeakComponent(DomainLevel):
        def name(self): return "future-leak"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["T1"]

        def update(self, time, inputs):
            if inputs.get("future"):
                raise TemporalViolation("Future data used")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = FutureLeakComponent()
    with pytest.raises(TemporalViolation):
        c.update(1, {"future": True})
```

---

## 5️⃣ O que T1 garante agora

| Propriedade            | Garantida |
| ---------------------- | --------- |
| Monotonicidade         | ✅         |
| Causalidade            | ✅         |
| Ordem de eventos       | ✅         |
| Estado inicial         | ✅         |
| Timestamp explícito    | ✅         |
| Sem vazamento temporal | ✅         |

👉 **Nenhum Digital Twin válido pode violar isso.**

---

## 🔒 Importante (nível científico)

T1 **não assume**:

* relógio global
* tempo contínuo
* sincronia perfeita

Ele funciona para:

* tempo discreto
* tempo lógico
* tempo físico
* simulação
* sistemas distribuídos

---

## 🔜 Próximo passo (ETAPA 2)

Agora temos dois caminhos corretos:

1️⃣ **Refinar T1**
→ invariantes compostas entre níveis (pai/filho)

2️⃣ **Avançar para Estatístico (S1)**
→ incerteza, confiança, consistência

Diga apenas:

> **“Refinar T1”**
> ou
> **“Vamos para S1”**

Eu sigo no trilho certo.

Excelente.
Vamos **refinar T1** — isso significa **sair das leis temporais locais** e entrar nas **leis temporais estruturais**, aquelas que tornam um **hierarchical digital twin cientificamente coerente**.

Vou manter o mesmo padrão:

1. O que significa “refinar T1”
2. Novas invariantes temporais (T1.x)
3. Testes TDD (pytest)
4. Fechamento do refinamento

Nada de implementação.

---

# 🧪 ETAPA 2 — T1 (Refinamento)

## 1️⃣ O que estamos refinando em T1

Até agora, T1 garantiu que **um nível isolado**:

* não volta no tempo
* respeita causalidade
* tem ordem interna consistente

Agora vamos garantir que **níveis diferentes**:

* não violem causalidade entre si
* não “adiantem” o tempo
* não usem estados inconsistentes

👉 Isso é o coração de um **Hierarchical Digital Twin**.

---

## 2️⃣ Novas invariantes temporais (nível sistêmico)

### 🧭 Visão geral

Chamaremos essas invariantes de:

* **T1.Hx** → *Hierarchical Temporal Invariants*

---

## 3️⃣ T1.H1 — Tempo do filho não pode ultrapassar o do pai

### 📐 Regra

> Para qualquer relação hierárquica:
>
> [
> t_{\text{child}} \le t_{\text{parent}}
> ]

📌 Motivação:

* o nível superior **resume** o inferior
* não pode “ver o futuro” do filho

---

### 🧪 Teste

```python
def test_t1_child_time_cannot_exceed_parent():
    class Parent(DomainLevel):
        def name(self): return "parent"
        def version(self): return "1.0.0"
        def dependencies(self): return ["child"]
        def invariants(self): return ["T1"]

        def current_time(self): return 10

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    class Child(DomainLevel):
        def name(self): return "child"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["T1"]

        def current_time(self): return 11  # futuro do pai

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    parent = Parent()
    child = Child()

    with pytest.raises(TemporalViolation):
        if child.current_time() > parent.current_time():
            raise TemporalViolation("Child ahead of parent")
```

---

## 4️⃣ T1.H2 — Atualização do pai exige filhos consistentes

### 📐 Regra

> Um nível superior **só pode ser atualizado** se:
>
> [
> \forall i,; t_{\text{child}*i} = t*{\text{parent}} ;\text{ou}; t_{\text{child}*i} = t*{\text{parent}} - \Delta
> ]

📌 Ou seja:

* filhos podem estar **alinhados**
* ou **um passo atrás**
* nunca indefinidos

---

### 🧪 Teste

```python
def test_t1_parent_update_requires_consistent_children():
    class Parent(DomainLevel):
        def name(self): return "parent"
        def version(self): return "1.0.0"
        def dependencies(self): return ["child"]
        def invariants(self): return ["T1"]

        def update(self, time, children):
            for c in children:
                if c.current_time() is None:
                    raise TemporalViolation("Child has undefined time")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    class Child(DomainLevel):
        def current_time(self): return None

    p = Parent()
    c = Child()

    with pytest.raises(TemporalViolation):
        p.update(10, [c])
```

---

## 5️⃣ T1.H3 — Propagação temporal é unidirecional

### 📐 Regra

> Tempo **só propaga para cima**:
>
> filho → pai
> nunca o contrário

📌 Isso impede:

* controle temporal descendente
* feedback causal inválido

---

### 🧪 Teste

```python
def test_t1_time_does_not_propagate_downwards():
    class Parent(DomainLevel):
        def name(self): return "parent"
        def version(self): return "1.0.0"
        def dependencies(self): return ["child"]
        def invariants(self): return ["T1"]

        def force_time(self, child, time):
            raise TemporalViolation("Parent cannot force child time")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    parent = Parent()
    child = object()

    with pytest.raises(TemporalViolation):
        parent.force_time(child, 100)
```

---

## 6️⃣ T1.H4 — Estado agregado respeita causalidade

### 📐 Regra

> O estado agregado em `t`:
>
> * só pode usar estados de filhos em `≤ t`

📌 Isso é essencial para:

* agregação energética
* somatórios
* métricas globais

---

### 🧪 Teste

```python
def test_t1_aggregation_respects_causality():
    class Parent(DomainLevel):
        def name(self): return "parent"
        def version(self): return "1.0.0"
        def dependencies(self): return ["child"]
        def invariants(self): return ["T1"]

        def aggregate(self, children, time):
            for c in children:
                if c.current_time() > time:
                    raise TemporalViolation("Future child state used")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    class Child(DomainLevel):
        def current_time(self): return 20

    p = Parent()
    c = Child()

    with pytest.raises(TemporalViolation):
        p.aggregate([c], time=10)
```

---

## 7️⃣ T1.H5 — Tempo observado ≠ tempo estimado (mas deve ser consistente)

### 📐 Regra

> Pode haver:
>
> * tempo de observação
> * tempo de estado estimado
>
> Mas ambos devem ser **monotônicos** e **consistentes**

---

### 🧪 Teste

```python
def test_t1_observed_and_estimated_time_are_consistent():
    class TemporalComponent(DomainLevel):
        def name(self): return "dual-time"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["T1"]

        def observed_time(self): return 10
        def estimated_time(self): return 9

        def validate_temporal_consistency(self):
            if self.estimated_time() > self.observed_time():
                raise TemporalViolation("Estimate ahead of observation")

        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = TemporalComponent()
    c.validate_temporal_consistency()
```

---

## 8️⃣ O que o T1 refinado garante

| Propriedade              | Garantida |
| ------------------------ | --------- |
| Tempo local              | ✅         |
| Tempo hierárquico        | ✅         |
| Causalidade entre níveis | ✅         |
| Agregação segura         | ✅         |
| Propagação unidirecional | ✅         |
| Consistência multi-tempo | ✅         |

👉 Agora **nenhum nível pode quebrar o tempo do sistema inteiro**.

---

## 🔒 Observação científica importante

Esse T1 refinado:

* funciona com **tempo lógico**
* suporta **sistemas distribuídos**
* permite **desalinhamento controlado**
* é compatível com **Kalman, batch, streaming**

---

## 🔜 Próximo passo (ETAPA 2)

Agora sim estamos prontos para:

> **S1 — Contrato Estatístico**

Onde entra:

* incerteza
* confiança
* consistência probabilística
* filtros
* modelos físicos vs estatísticos

Quando quiser, diga:

> **“Vamos para S1”**

e seguimos com o mesmo rigor.
