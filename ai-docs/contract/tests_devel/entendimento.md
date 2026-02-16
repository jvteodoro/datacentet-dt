Perfeito. Antes de escrever **qualquer linha de código**, vou explicitar **meu entendimento da tarefa**, **o escopo exato**, e **os padrões que seguirei** para organização de arquivos, testes e dependências. Isso evita desalinhamento metodológico — especialmente importante agora que temos um **baseline congelado**.

---

# 🧠 Meu entendimento da tarefa

## 🎯 Objetivo da etapa atual

Você quer **mapear o catálogo congelado de invariantes** (SW, T, S, E, M, H) em **testes de propriedade** (*property-based testing*), de modo que:

* Cada **invariante** tenha **uma ou mais propriedades testáveis**
* Os testes **não dependam de implementações concretas**
* Os testes validem **leis do sistema**, não exemplos pontuais
* O sistema falhe **para qualquer contraexemplo**, não apenas casos escolhidos à mão

Em outras palavras:

> Estamos transformando **leis formais do domínio** em **propriedades universais verificáveis**.

Isso é exatamente o uso correto do **Hypothesis**.

---

## 🧩 Escopo do que FAREMOS (e do que NÃO faremos)

### ✅ Vamos fazer agora

* Mapear **cada invariante** → **classe de propriedades**
* Definir **estratégias de geração** (válidas e inválidas)
* Criar testes **genéricos**, reutilizáveis
* Testar **contratos**, não implementações

### ❌ Não vamos fazer agora

* Implementar DomainLevel real
* Implementar filtros, modelos ou lógica física
* Escrever testes unitários tradicionais (example-based)
* Otimizar performance dos testes

---

## 🧱 Estratégia geral de mapeamento

Vou usar este padrão mental:

```
Invariante → Lei → Propriedade → Contraexemplo gerado
```

Exemplo:

* **T2 (monotonicidade temporal)**
* Lei: tempo nunca retrocede
* Propriedade: para toda sequência gerada, t[i+1] ≥ t[i]
* Contraexemplo: sequência com regressão → deve falhar

---

# 🧪 Estratégia de testes de propriedade

## Por que Hypothesis (e não pytest puro)

Porque invariantes são:

* universais
* independentes de valores específicos
* mais bem testados por **exploração do espaço de estados**

Hypothesis permite:

* geração automática de contraexemplos
* shrinking (mínimo contraexemplo)
* testes verdadeiramente declarativos

---

# 📁 Padrão de organização de arquivos

Vou seguir **estritamente** este padrão (sem variações):

```text
tests/
 └── properties/
      ├── software/
      │    └── test_sw_properties.py
      ├── temporal/
      │    └── test_t_properties.py
      ├── statistical/
      │    └── test_s_properties.py
      ├── epistemic/
      │    └── test_e_properties.py
      ├── model/
      │    └── test_m_properties.py
      └── hierarchy/
           └── test_h_properties.py
```

### Por quê esse padrão?

* 1 pasta = 1 tipo de contrato
* Facilita auditoria
* Facilita desligar/ligar famílias de testes
* Facilita evolução versionada

---

# 🧩 Padrão de apresentação de código (importantíssimo)

Sempre que eu escrever código, seguirei **exatamente este formato**:

---

## 📄 Arquivo

```text
tests/properties/temporal/test_t_properties.py
```

## 📦 Dependências

```python
import pytest
from hypothesis import given, strategies as st
```

(Se houver dependências adicionais, elas serão **explicitadas antes do código**)

## 🧪 Código do teste

```python
@given(...)
def test_...( ... ):
    ...
```

---

Nunca vou:

* omitir imports
* misturar arquivos
* esconder dependências implícitas
* colar múltiplos arquivos no mesmo bloco

---

# 📦 Dependências que assumirei (e sempre declararei)

Para esta etapa, **apenas**:

```text
pytest
hypothesis
numpy   (somente em invariantes estatísticos)
```

❗ Nada de:

* pandas
* sklearn
* frameworks de ML
* libs de controle

---

# 🧠 Abstrações usadas nos testes

Como **não temos implementação real**, usaremos:

* **Fakes mínimos**
* **Stubs epistêmicos**
* **Objetos de domínio artificiais**

Esses objetos:

* só existem dentro dos testes
* não vazam para o domínio
* são descartáveis
* existem apenas para violar ou satisfazer propriedades

---

# 🧪 Padrão de nomenclatura dos testes

Sempre:

```
test_<invariant>_<propriedade>_<resultado>
```

Exemplos:

* `test_T2_time_monotonicity_is_never_violated`
* `test_S3_confidence_out_of_bounds_is_rejected`
* `test_H3_parent_uncertainty_not_smaller_than_children`

---

# 🧩 Ordem em que proponho avançar

Para manter estabilidade cognitiva e técnica:

1️⃣ **Software (SW)** — propriedades estruturais simples
2️⃣ **Temporal (T)** — propriedades de sequência
3️⃣ **Statistical (S)** — propriedades matemáticas
4️⃣ **Epistemic (E)** — propriedades semânticas
5️⃣ **Model (M)** — propriedades compostas
6️⃣ **Hierarchy (H)** — propriedades emergentes

👉 Essa ordem reduz o risco de circularidade nos testes.

---

# ✅ Checklist de alinhamento

Antes de prosseguir, valide mentalmente se:

* [x] Estamos testando **leis**, não exemplos
* [x] Os testes são **agnósticos à implementação**
* [x] O padrão de arquivos é aceitável
* [x] O uso de Hypothesis faz sentido
* [x] Nada do baseline congelado será reaberto

---

## Próximo passo (só após sua confirmação)

Quando você disser:

> **“Pode prosseguir”**

eu começo **imediatamente** com:

👉 **Software Contract (SW) → testes de propriedade**,
seguindo exatamente os padrões descritos acima.

Se quiser ajustar **qualquer detalhe do plano**, este é o momento certo.
