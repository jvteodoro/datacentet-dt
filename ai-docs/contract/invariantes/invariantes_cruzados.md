Perfeito. Vou **seguir exatamente o caminho 1 → 2 → 3**, com calma, rigor e **sem pular etapas**.
Neste passo **não vamos escrever testes nem código**, apenas **definir formalmente os invariantes cruzados** do `DomainLevel`.

Pense nisso como a **constituição do seu Digital Twin**:
antes de testar ou implementar, precisamos dizer **o que nunca pode ser violado**.

---

# ETAPA 1 — Invariantes cruzadas do `DomainLevel`

## 1. O que são invariantes cruzadas?

Até agora, cada contrato responde a uma pergunta específica:

| Contrato    | Pergunta                         |
| ----------- | -------------------------------- |
| Epistêmico  | *O que eu sei é válido?*         |
| Temporal    | *Quando isso é válido?*          |
| Estatístico | *Quão confiável é?*              |
| Software    | *O componente está operacional?* |

👉 **Invariantes cruzadas** são regras que **dependem de mais de um contrato ao mesmo tempo**.

Exemplo simples:

> “Não adianta o estado ser estatisticamente válido se ele está temporalmente obsoleto.”

Isso envolve **estatística + tempo**.

---

## 2. Classificação das invariantes cruzadas

Vamos organizar as invariantes em **5 grupos**, para manter clareza e permitir testes depois:

1. Invariantes de **Estado**
2. Invariantes de **Tempo**
3. Invariantes de **Conhecimento (Epistêmicas)**
4. Invariantes de **Interface Hierárquica**
5. Invariantes de **Operação do Software**

Cada grupo terá:

* descrição conceitual
* forma lógica
* implicações arquiteturais

---

# 1️⃣ Invariantes de Estado

### **Invariant S1 — Estado epistemicamente válido**

**Descrição**
Todo estado exposto pelo `DomainLevel` deve ser epistemicamente justificável.

**Forma lógica**

```
validate_state_knowledge(state) == True
```

**Implica**

* o estado veio de um estimador admissível
* não é um valor arbitrário ou não inicializado

---

### **Invariant S2 — Estado estatisticamente admissível**

**Descrição**
O estado deve possuir uma representação estatística válida.

**Forma lógica**

```
validate_distribution(state) == True
covariance(state) is PSD
confidence(state) ∈ (0, 1]
```

**Implica**

* o estado carrega incerteza explícita
* não existe “estado determinístico mágico”

---

### **Invariant S3 — Estado suficiente**

**Descrição**
O estado deve ser suficiente para previsão e controle no horizonte do domínio.

**Forma conceitual**

> Não deve existir variável dinâmica essencial fora do estado.

**Implica**

* escolha criteriosa de variáveis de estado
* evita “estado incompleto” que exige hacks externos

---

# 2️⃣ Invariantes Temporais

### **Invariant T1 — Coerência temporal do estado**

**Descrição**
Todo estado tem um timestamp associado e coerente.

**Forma lógica**

```
state_timestamp() <= current_time()
```

---

### **Invariant T2 — Monotonicidade temporal**

**Descrição**
Atualizações de estado não podem retroceder no tempo.

**Forma lógica**

```
new_state_time >= previous_state_time
```

---

### **Invariant T3 — Frescor do estado**

**Descrição**
Estados obsoletos não podem ser usados para decisão.

**Forma lógica**

```
current_time() - last_update_time() <= max_staleness()
```

**Implica**

* proteção contra sensores mortos
* proteção contra travamentos silenciosos

---

# 3️⃣ Invariantes Epistêmicas

### **Invariant E1 — Não extrapolação de conhecimento**

**Descrição**
O `DomainLevel` não pode expor variáveis fora de seu escopo epistemológico.

**Forma lógica**

```
∀ k ∈ public_view(): k ∈ knowledge_scope()
```

---

### **Invariant E2 — Assunções válidas**

**Descrição**
Os modelos só são válidos enquanto suas assunções forem válidas.

**Forma lógica**

```
validate_assumptions() == True
```

**Implica**

* detecção de regime inválido
* possibilidade de degradação graciosa

---

### **Invariant E3 — Identificáveis epistemicamente justificados**

**Descrição**
Parâmetros identificáveis só podem ser usados se houver evidência suficiente.

**Forma conceitual**

> Identificável ≠ conhecido por default

---

# 4️⃣ Invariantes de Interface Hierárquica

### **Invariant H1 — Encapsulamento hierárquico**

**Descrição**
Um nível superior só pode acessar o `public_view`.

**Forma lógica**

```
parent_access ⊆ public_view()
```

---

### **Invariant H2 — Independência de implementação**

**Descrição**
Mudanças internas não podem quebrar o contrato público.

**Implica**

* versionamento
* estabilidade de API
* compatibilidade retroativa

---

### **Invariant H3 — Consistência entre níveis**

**Descrição**
Observáveis agregados devem ser consistentes com os filhos.

**Forma conceitual**

> O pai não pode contradizer sistematicamente os filhos.

(Esse será ótimo para testes estatísticos depois.)

---

# 5️⃣ Invariantes de Software

### **Invariant SW1 — Ciclo de vida válido**

**Descrição**
Nenhuma operação pode ocorrer antes da inicialização.

**Forma lógica**

```
is_initialized() == True
```

---

### **Invariant SW2 — Saúde operacional**

**Descrição**
Componentes degradados não podem atuar como fonte confiável.

**Forma lógica**

```
health_status() ∈ {"healthy", "degraded"}
```

---

### **Invariant SW3 — Falhas contidas**

**Descrição**
Falhas internas não podem corromper o estado global.

**Implica**

* exceções explícitas
* rollback de estado
* isolamento de falhas

---

# 3. Invariante Mestra (a mais importante)

### **Invariant M — Estado publicável**

Um estado **só pode ser exposto ou usado para controle se TODAS forem verdadeiras**:

```
Epistemic ✓
Temporal ✓
Statistical ✓
Software ✓
```

Ou seja:

> **Não existe estado “meio válido”.**

---

# 4. Por que isso é fundamental antes dos testes?

Porque agora:

* sabemos **o que testar**
* sabemos **quando falhar**
* sabemos **qual contrato foi violado**

Isso evita:

* testes frágeis
* validações redundantes
* lógica espalhada

---

## Próximo passo (ETAPA 2)

👉 **Escrever testes TDD para essas invariantes**, começando por:

* invariantes simples (SW1, T1)
* depois invariantes compostas (M, H3)

Quando você disser **“vamos para a etapa 2”**, eu:

* organizo os testes
* explico a estratégia
* escrevo o primeiro conjunto de testes em pytest

Sem pressa, com rigor.
