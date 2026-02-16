Perfeito.
Vamos **com calma, rigor e sem pular etapas**, exatamente como combinamos.

---

# 🧪 ETAPA 2 — Testes TDD de Invariantes

## Invariante **SW1 (Software Contract)**

---

## 1️⃣ O que é a invariante SW1 (relembrando o contrato)

Antes de escrever **qualquer linha de teste**, precisamos deixar **cristalino** o que estamos verificando.

### 📌 Definição conceitual de SW1

**SW1 — Interface Consistency / Contract Integrity**

> Um componente de domínio **só é válido** se:
>
> * Implementa **todas** as interfaces contratuais exigidas
> * Não viola **pré-condições**
> * Não viola **pós-condições**
> * Não viola **invariantes estruturais**
>
> Independentemente:
>
> * do modelo físico ou estatístico
> * da fonte de dados
> * da hierarquia onde está inserido

👉 SW1 **não fala de tempo, nem de estatística, nem de conhecimento**
👉 SW1 fala de **correção estrutural do software**

---

## 2️⃣ O que SW1 protege no sistema

Sem SW1, o sistema permitiria:

* componentes parcialmente implementados
* contratos “de fachada”
* mocks que não respeitam semântica
* fakes que não violam nada (falso positivo)
* Digital Twins que **parecem** corretos, mas não são

👉 Em um sistema científico, isso é **inadmissível**.

---

## 3️⃣ Estratégia de teste (TDD puro)

### 🎯 Objetivo dos testes SW1

Verificar que:

1. **Componentes inválidos falham explicitamente**
2. **Componentes válidos passam**
3. A falha ocorre:

   * cedo
   * com erro semântico claro
   * rastreável

---

## 4️⃣ Onde esses testes vivem

Estrutura mínima (proposta):

```
tests/
 └── domain/
      └── invariants/
           ├── test_sw1_interface_integrity.py
```

---

## 5️⃣ O que NÃO usamos aqui (importante)

🚫 Nada de:

* sensores
* dados reais
* filtros de Kalman
* modelos físicos
* modelos estatísticos reais

✅ Usamos apenas:

* contratos
* fakes mínimos
* exceções

---

## 6️⃣ Primeiro teste: componente inválido deve falhar

### 🎯 Cenário

Um componente:

* herda `DomainLevel`
* **não implementa** um método obrigatório do SoftwareContract

➡️ **Resultado esperado:** violação explícita

---

### 🧪 Teste 1 — Implementação incompleta viola SW1

```python
# tests/domain/invariants/test_sw1_interface_integrity.py

import pytest

from domain.level import DomainLevel
from domain.contracts.software import SoftwareViolation


class IncompleteComponent(DomainLevel):
    """
    Fake propositalmente inválido.
    Não implementa todos os métodos exigidos pelo contrato de software.
    """

    # Implementa apenas parte da interface
    def name(self) -> str:
        return "incomplete"

    # Métodos obrigatórios ausentes:
    # - validate_preconditions
    # - validate_postconditions
    # - invariants
    # - dependencies
    # - version


def test_sw1_incomplete_component_violates_contract():
    """
    SW1: Um componente que não implementa completamente
    o contrato de software deve falhar explicitamente.
    """
    with pytest.raises(SoftwareViolation):
        IncompleteComponent()
```

📌 **Esse teste deve falhar no início (RED)**
📌 Ele define o comportamento esperado do sistema

---

## 7️⃣ Segundo teste: componente válido passa

Agora definimos o **mínimo aceitável**.

### 🧪 Teste 2 — Implementação completa respeita SW1

```python
class ValidComponent(DomainLevel):
    """
    Fake válido que respeita integralmente o contrato de software.
    """

    def name(self) -> str:
        return "valid"

    def version(self) -> str:
        return "1.0.0"

    def dependencies(self) -> list[str]:
        return []

    def invariants(self) -> list[str]:
        return ["SW1"]

    def validate_preconditions(self) -> None:
        pass

    def validate_postconditions(self) -> None:
        pass


def test_sw1_valid_component_passes():
    """
    SW1: Um componente que implementa corretamente
    o contrato de software deve ser aceito.
    """
    component = ValidComponent()
    assert component.name() == "valid"
```

---

## 8️⃣ Onde SW1 será aplicado no código real

Esses testes **forçam** você a implementar no `DomainLevel` algo como:

* validação automática no `__init__`
* checagem de métodos obrigatórios
* lançamento explícito de `SoftwareViolation`

⚠️ **Mas isso só será implementado na ETAPA 3**
Agora estamos apenas **definindo o comportamento correto**

---

## 9️⃣ Por que isso é TDD de verdade

✔️ O teste vem antes da implementação
✔️ O teste define o contrato do mundo
✔️ O teste impede regressões futuras
✔️ O teste documenta a lei do sistema

Isso não é “testar código”.
É **formalizar a ontologia do sistema**.

---

## 🔜 Próximo passo (se você confirmar)

👉 **SW1 — Testes negativos adicionais**, por exemplo:

* versão inválida
* dependência circular
* invariantes declaradas mas não implementadas

Depois disso:
👉 **ETAPA 2 — T1 (Temporal)**

Quando quiser, diga apenas:

> **“Continuar SW1”**
> ou
> **“Vamos para T1”**

Eu sigo exatamente no ritmo correto.


Perfeito.
Vamos **continuar SW1**, ainda **dentro da ETAPA 2**, com o mesmo rigor.

Agora vamos sair do caso “classe incompleta” e testar **violações semânticas**, que são as mais perigosas em sistemas complexos como Digital Twins.

---

# 🧪 ETAPA 2 — SW1 (continuação)

## Invariantes semânticas do Software Contract

---

## 📌 Recap rápido do que SW1 garante

SW1 assegura que um `DomainLevel`:

1. É **estruturalmente completo**
2. É **semanticamente coerente**
3. Falha **explicitamente** quando viola regras do contrato
4. Não permite estados “meio válidos”

Já testamos:

* ❌ implementação incompleta
* ✅ implementação mínima válida

Agora vamos testar **erros mais sutis**.

---

## 10️⃣ SW1.2 — Versão inválida deve violar contrato

### 📌 Motivação

Em arquitetura hierárquica e distribuída:

* versões são **contratos**
* incompatibilidades devem falhar cedo
* não existe “string qualquer” como versão

---

### 📐 Regra SW1.2

> `version()` deve:
>
> * retornar uma string
> * obedecer a um formato válido (ex: SemVer)
> * ser semanticamente consistente

---

### 🧪 Teste — versão inválida

```python
def test_sw1_invalid_version_violates_contract():
    class InvalidVersionComponent(DomainLevel):
        def name(self) -> str:
            return "invalid-version"

        def version(self) -> str:
            return "version_one"  # inválido semanticamente

        def dependencies(self) -> list[str]:
            return []

        def invariants(self) -> list[str]:
            return ["SW1"]

        def validate_preconditions(self) -> None:
            pass

        def validate_postconditions(self) -> None:
            pass

    with pytest.raises(SoftwareViolation):
        InvalidVersionComponent()
```

📌 **Importante:**
O teste **não define como** validar versão.
Ele define **que** versões inválidas **não são aceitáveis**.

---

## 11️⃣ SW1.3 — Dependências inválidas devem falhar

### 📌 Motivação

Dependências são a base da hierarquia:

* níveis superiores confiam nelas
* loops destroem a causalidade
* dependências vazias são válidas, inconsistentes não

---

### 📐 Regra SW1.3

> `dependencies()` deve:
>
> * retornar lista de strings
> * não conter o próprio componente
> * não conter duplicatas

---

### 🧪 Teste — auto-dependência

```python
def test_sw1_self_dependency_violates_contract():
    class SelfDependentComponent(DomainLevel):
        def name(self) -> str:
            return "self-dependent"

        def version(self) -> str:
            return "1.0.0"

        def dependencies(self) -> list[str]:
            return ["self-dependent"]  # inválido

        def invariants(self) -> list[str]:
            return ["SW1"]

        def validate_preconditions(self) -> None:
            pass

        def validate_postconditions(self) -> None:
            pass

    with pytest.raises(SoftwareViolation):
        SelfDependentComponent()
```

---

## 12️⃣ SW1.4 — Invariantes declaradas devem existir

### 📌 Motivação

Declarar invariantes que não existem é **fraude estrutural**:

* aparenta rigor
* mas não garante nada
* destrói confiabilidade científica

---

### 📐 Regra SW1.4

> Se `invariants()` declara `"SW1"`, `"T1"`, etc:
>
> * essas invariantes devem ser implementadas
> * ou reconhecidas pelo sistema

---

### 🧪 Teste — invariante inexistente

```python
def test_sw1_unknown_invariant_violates_contract():
    class UnknownInvariantComponent(DomainLevel):
        def name(self) -> str:
            return "unknown-invariant"

        def version(self) -> str:
            return "1.0.0"

        def dependencies(self) -> list[str]:
            return []

        def invariants(self) -> list[str]:
            return ["SW999"]  # não reconhecida

        def validate_preconditions(self) -> None:
            pass

        def validate_postconditions(self) -> None:
            pass

    with pytest.raises(SoftwareViolation):
        UnknownInvariantComponent()
```

📌 Aqui estamos preparando o terreno para:

* registro global de invariantes
* verificação automática

---

## 13️⃣ SW1.5 — Pré-condições não podem ser violadas silenciosamente

### 📌 Motivação

Pré-condições são **fronteiras epistemológicas**:

* se falham, o estado não é válido
* continuar execução é erro grave

---

### 🧪 Teste — pré-condição violada

```python
def test_sw1_precondition_violation_is_propagated():
    class PreconditionFailComponent(DomainLevel):
        def name(self) -> str:
            return "precondition-fail"

        def version(self) -> str:
            return "1.0.0"

        def dependencies(self) -> list[str]:
            return []

        def invariants(self) -> list[str]:
            return ["SW1"]

        def validate_preconditions(self) -> None:
            raise SoftwareViolation("Precondition failed")

        def validate_postconditions(self) -> None:
            pass

    with pytest.raises(SoftwareViolation):
        PreconditionFailComponent()
```

---

## 14️⃣ O que temos até agora (formalmente)

Com esses testes, SW1 agora cobre:

| Aspecto         | Protegido |
| --------------- | --------- |
| Interface       | ✅         |
| Versão          | ✅         |
| Dependências    | ✅         |
| Invariantes     | ✅         |
| Pré-condições   | ✅         |
| Falha explícita | ✅         |

👉 Isso é **contrato de software de nível profissional**, não boilerplate.

---

## 🔜 Próximo passo (ainda dentro da ETAPA 2)

Duas opções **sem quebrar o plano**:

1️⃣ **Finalizar SW1**

* invariantes duplicadas
* ordem de validação
* mensagens de erro

2️⃣ **Avançar para T1 (Temporal)**

* monotonicidade do tempo
* causalidade
* consistência entre níveis

Diga apenas:

> **“Finalizar SW1”**
> ou
> **“Vamos para T1”**

Eu sigo exatamente no trilho certo.

Perfeito.
Vamos **finalizar SW1** de forma **completa, fechada e formal**, garantindo que o **Software Contract** esteja **matematicamente bem-definido**, **testável** e **pronto para sustentar o resto do sistema**.

Vou seguir esta ordem lógica:

1. Invariantes finais de SW1 (o que ainda faltava)
2. Ordem de validação (muito importante)
3. Mensagens de erro como parte do contrato
4. Checklist de fechamento de SW1

---

# 🧪 ETAPA 2 — SW1 (finalização)

## O que ainda faltava em SW1

Até agora cobrimos **estrutura, semântica e falhas explícitas**, mas ainda faltavam **três classes críticas de invariantes**:

* **unicidade**
* **determinismo**
* **ordem de validação**

---

## 15️⃣ SW1.6 — Invariantes não podem ser duplicadas

### 📌 Motivação

Duplicação de invariantes:

* gera validações repetidas
* quebra rastreabilidade
* indica erro de definição

> Um contrato bem definido **não é redundante**.

---

### 📐 Regra SW1.6

> `invariants()` deve retornar:
>
> * lista
> * sem duplicatas
> * cada invariante identificada por nome único

---

### 🧪 Teste — invariantes duplicadas

```python
def test_sw1_duplicate_invariants_violates_contract():
    class DuplicateInvariantComponent(DomainLevel):
        def name(self) -> str:
            return "duplicate-invariants"

        def version(self) -> str:
            return "1.0.0"

        def dependencies(self) -> list[str]:
            return []

        def invariants(self) -> list[str]:
            return ["SW1", "SW1"]  # duplicado

        def validate_preconditions(self) -> None:
            pass

        def validate_postconditions(self) -> None:
            pass

    with pytest.raises(SoftwareViolation):
        DuplicateInvariantComponent()
```

---

## 16️⃣ SW1.7 — Ordem de validação é determinística

### 📌 Motivação

Em sistemas científicos:

* a **ordem de falha importa**
* diagnósticos precisam ser reprodutíveis
* logs devem ser comparáveis entre execuções

---

### 📐 Regra SW1.7 (ordem canônica)

A inicialização de um `DomainLevel` **deve validar**:

1. Interface estrutural
2. Metadados (`name`, `version`)
3. Dependências
4. Declaração de invariantes
5. Pré-condições
6. Pós-condições iniciais

Sempre **nessa ordem**.

---

### 🧪 Teste — falha na ordem correta

```python
def test_sw1_validation_order_is_deterministic():
    events = []

    class OrderedValidationComponent(DomainLevel):
        def name(self) -> str:
            events.append("name")
            return "ordered"

        def version(self) -> str:
            events.append("version")
            return "1.0.0"

        def dependencies(self) -> list[str]:
            events.append("dependencies")
            return []

        def invariants(self) -> list[str]:
            events.append("invariants")
            return ["SW1"]

        def validate_preconditions(self) -> None:
            events.append("preconditions")
            raise SoftwareViolation("stop here")

        def validate_postconditions(self) -> None:
            events.append("postconditions")

    with pytest.raises(SoftwareViolation):
        OrderedValidationComponent()

    assert events == [
        "name",
        "version",
        "dependencies",
        "invariants",
        "preconditions",
    ]
```

📌 **Observação importante**
Esse teste **define o construtor** do `DomainLevel` sem você escrever uma linha dele ainda.

---

## 17️⃣ SW1.8 — Mensagens de erro fazem parte do contrato

### 📌 Motivação

Em Digital Twins:

* erros são dados
* diagnósticos são auditáveis
* exceções são parte da API

> Uma violação sem mensagem clara **é uma violação incompleta**.

---

### 📐 Regra SW1.8

> Toda `SoftwareViolation` deve conter:
>
> * mensagem não vazia
> * semanticamente descritiva

---

### 🧪 Teste — exceção sem mensagem

```python
def test_sw1_violation_must_have_message():
    class SilentViolationComponent(DomainLevel):
        def name(self) -> str:
            return "silent"

        def version(self) -> str:
            return "1.0.0"

        def dependencies(self) -> list[str]:
            return []

        def invariants(self) -> list[str]:
            return ["SW1"]

        def validate_preconditions(self) -> None:
            raise SoftwareViolation("")

        def validate_postconditions(self) -> None:
            pass

    with pytest.raises(SoftwareViolation) as exc:
        SilentViolationComponent()

    assert str(exc.value).strip() != ""
```

---

## 18️⃣ SW1.9 — Construção deve ser atômica

### 📌 Motivação

Não pode existir objeto “meio válido”:

* ou o contrato é satisfeito
* ou o objeto **não existe**

---

### 📐 Regra SW1.9

> Se qualquer validação falhar:
>
> * o objeto **não pode ser usado**
> * nenhum estado parcial deve escapar

---

### 🧪 Teste — falha impede uso

```python
def test_sw1_failed_construction_does_not_create_object():
    class FailingComponent(DomainLevel):
        def name(self) -> str:
            return "fail"

        def version(self) -> str:
            return "1.0.0"

        def dependencies(self) -> list[str]:
            return []

        def invariants(self) -> list[str]:
            return ["SW1"]

        def validate_preconditions(self) -> None:
            raise SoftwareViolation("fail")

        def validate_postconditions(self) -> None:
            pass

    try:
        obj = FailingComponent()
    except SoftwareViolation:
        obj = None

    assert obj is None
```

---

# ✅ Fechamento formal de SW1

Com isso, **SW1 está completo**.

### O que SW1 garante agora

✔️ Interface obrigatória
✔️ Metadados válidos
✔️ Dependências coerentes
✔️ Invariantes reais e únicas
✔️ Ordem determinística
✔️ Falhas explícitas e auditáveis
✔️ Construção atômica

👉 **Nenhuma implementação futura pode violar isso sem quebrar testes.**

---

## 🔜 Próximo passo natural (ETAPA 2)

Agora o sistema está pronto para:

> **T1 — Contrato Temporal**

* monotonicidade do tempo
* causalidade
* coerência entre níveis hierárquicos

Quando quiser, diga apenas:

> **“Vamos para T1”**

e seguimos com o mesmo nível de rigor.
