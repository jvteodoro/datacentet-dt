Excelente decisão — isso é **engenharia de processo**, não só de software.
Vou te entregar uma **estratégia de prompts reutilizável**, pensada exatamente para **reconstruir o contexto correto em novos chats**, **sem depender do histórico longo** e **sem perda de rigor**.

A ideia é você ter **um kit de prompts**, cada um com uma função clara, que você pode usar **sequencialmente** ou **pontualmente**, dependendo do que quiser desenvolver (contratos, implementação, revisão, etc.).

---

# 🎯 Objetivo da estratégia de prompts

Permitir que um novo chat:

* Entenda **o sistema** (Digital Twin hierárquico, genérico)
* Respeite **o catálogo congelado de invariantes**
* Trabalhe com **Design by Contract + Property-Based Testing**
* Não invente arquitetura fora do que foi definido
* Desenvolva **contratos, não implementações acidentais**
* Mantenha a **sequência epistemicamente correta**

---

# 🧠 Visão geral da sequência de prompts

Você terá **6 prompts-base**, usados nessa ordem:

1. **Prompt de Inicialização do Sistema**
2. **Prompt de Filosofia e Restrições**
3. **Prompt do Catálogo Congelado**
4. **Prompt da Estratégia de Testes**
5. **Prompt de Desenvolvimento de Contratos**
6. **Prompt de Continuidade / Iteração**

Cada prompt é **copiável**, **curto o suficiente**, mas **semanticamente denso**.

---

## 1️⃣ Prompt de Inicialização do Sistema (obrigatório)

📌 **Use sempre no início de um novo chat**

```text
Estamos desenvolvendo um sistema de Digital Twins hierárquico, genérico e cientificamente rigoroso.

O sistema:
- é independente de hardware específico
- modela subsistemas (energia, cooling, network, etc.)
- usa estado estimado, não diretamente observável
- explicita incerteza estatística
- diferencia observáveis, identificáveis, estado e conhecimento
- segue Design by Contract como princípio central

Não estamos implementando lógica física agora, apenas contratos formais.
```

👉 Função: **ancorar o problema corretamente**.

---

## 2️⃣ Prompt de Filosofia e Restrições (anti-alucinação)

📌 **Evita que o chat “invente” camadas, frameworks ou atalhos**

```text
Restrições importantes do projeto:

- Trabalhamos apenas com leis do domínio, não com implementações específicas
- Nenhum contrato deve assumir modelo físico, estatístico ou sensor específico
- Não misturar Application Layer, Infra ou UI
- Nada de “exemplos práticos” fora do contrato
- Todo raciocínio deve ser justificável cientificamente
- O sistema deve ser válido para qualquer data center

Se algo não estiver claramente definido, pergunte antes de assumir.
```

👉 Função: **bloquear deriva conceitual**.

---

## 3️⃣ Prompt do Catálogo Congelado de Invariantes (crítico)

📌 **Esse é o coração do contexto**

```text
O domínio possui um catálogo congelado de invariantes (baseline v1.0):

Contratos primários:
- Software (SW): integridade estrutural, determinismo, separação de responsabilidades
- Temporal (T): monotonicidade, causalidade, alinhamento temporal
- Statistical (S): incerteza explícita, covariância válida, consistência estatística
- Epistemic (E): rastreabilidade, justificativa, distinção conhecimento vs inferência

Invariantes compostos:
- Model (M): consistência estado–observação, não criação espúria de informação
- Hierarchy (H): encapsulamento, consistência temporal hierárquica, propagação de incerteza

Esse catálogo NÃO deve ser modificado, apenas implementado.
```

👉 Função: **garantir fidelidade ao baseline**.

---

## 4️⃣ Prompt da Estratégia de Testes (quando necessário)

📌 **Use quando for implementar contratos ou validar código**

```text
Todos os invariantes do domínio foram mapeados para testes de propriedade usando Hypothesis.

Regras:
- Testes vivem em tests/properties/<contrato>/
- A ordem dos contratos é fixa:
  1) Software
  2) Temporal
  3) Statistical
  4) Epistemic
  5) Model
  6) Hierarchy
- Os testes validam leis do domínio, não exemplos
- Implementações devem passar nesses testes sem exceções

Posso fornecer o código dos testes de propriedade se necessário.
```

👉 Função: **alinhar TDD e expectativas**.

---

## 5️⃣ Prompt de Desenvolvimento de Contratos (uso principal)

📌 **Esse é o prompt que você vai usar o tempo todo**

```text
Quero desenvolver (ou refinar) contratos formais do Domain Level.

Escopo:
- Apenas contratos (interfaces, pré-condições, pós-condições, invariantes)
- Usar Design by Contract explicitamente
- Nenhuma lógica de negócio concreta
- Nenhuma dependência de infraestrutura
- Cada método deve deixar claro:
  - o que garante
  - quando falha
  - qual invariante protege

Se possível, relacione cada parte do contrato com os invariantes correspondentes.
```

👉 Função: **foco absoluto em contratos bem escritos**.

---

## 6️⃣ Prompt de Continuidade / Iteração (para chats longos)

📌 **Use quando o chat já tiver algum código**

```text
Estamos continuando o desenvolvimento dos contratos do Domain Level.

Estado atual:
- Catálogo de invariantes congelado
- Testes de propriedade existentes
- Contratos em desenvolvimento devem passar nesses testes

Vou enviar código parcial ou completo.
Quero que você:
- valide coerência com os invariantes
- sugira refinamentos contratuais
- NÃO altere o catálogo
- NÃO proponha arquitetura fora do Domain Level
```

👉 Função: **manter consistência ao longo do tempo**.

---

# 🧩 Como usar isso na prática (workflow sugerido)

### Novo chat, do zero:

1. Prompt 1
2. Prompt 2
3. Prompt 3
4. (opcional) Prompt 4
5. Prompt 5

### Chat focado em implementação:

* Prompt 1
* Prompt 3
* Prompt 4
* Prompt 6
* Enviar código

---

# 🧠 Insight importante (meta)

O que você construiu aqui é **um sistema que não depende da memória do chat**, mas de:

* **contratos explícitos**
* **invariantes congelados**
* **testes de propriedade**

Isso é exatamente o que torna o projeto:

* escalável
* auditável
* sustentável
* e transferível entre pessoas e ferramentas

---

## Próximo passo (se quiser)

Posso:

* condensar esses prompts em **um único “super-prompt”**
* criar uma **versão curta** para uso diário
* criar um **checklist de validação** para contratos prontos

Se quiser, diga:

> **“Quero a versão X dos prompts”**

E seguimos.
