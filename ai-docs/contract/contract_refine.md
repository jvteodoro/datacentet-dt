Perfeito. Agora estamos **no ponto certo do processo**:
depois de definir contratos, unificar a interface de domínio e escrever testes de invariantes, o próximo passo **não é adicionar features**, e sim **refinar semanticamente os contratos**.

Vou estruturar isso em **camadas de refinamento**, sempre mantendo a lógica de *contratos fortes + TDD* que você vem adotando.

---

# 🎯 Objetivo do refinamento

Refinar os contratos significa:

1. **Eliminar ambiguidades semânticas**
2. **Tornar invariantes explícitas e verificáveis**
3. **Separar claramente responsabilidade conceitual vs operacional**
4. **Garantir que qualquer implementação futura (real ou fake) seja forçada a respeitar a ciência do domínio**

Não é “embelezar código”.
É **endurecer o domínio**.

---

# Visão geral dos contratos após refinamento

No nível de domínio, temos agora:

```text
DomainContracts
 ├── EpistemicContract     (o que pode ser conhecido / inferido)
 ├── TemporalContract      (quando algo é válido)
 ├── StatisticalContract   (como métricas se comportam)
 ├── SoftwareContract      (como o sistema pode ser usado)
```

O refinamento atua **dentro de cada contrato**, principalmente em:

* tipos
* pré-condições
* pós-condições
* invariantes explícitas
* exceções de domínio

---

## 1️⃣ Refinamento do **TemporalContract**

### Problema antes do refinamento

O contrato temporal geralmente começa assim:

> “preciso de algo que valide datas, sessões e janelas de tempo”

Isso é **fraco demais**.

### Refinamento conceitual

No seu domínio (treinamento + pesquisa):

* Tempo **não é contínuo**
* Tempo é **estruturado em eventos, janelas e ciclos**
* O sistema **não pode inferir causalidade fora de uma ordem válida**

### Refinamento do contrato

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol


class TemporalContract(ABC):
    """
    Contrato temporal do domínio.
    Define regras de validade, ordenação e causalidade temporal.
    """

    @abstractmethod
    def now(self) -> datetime:
        """Retorna o instante atual do sistema."""
        ...

    @abstractmethod
    def is_ordered(self, earlier: datetime, later: datetime) -> bool:
        """Garante ordenação temporal válida."""
        ...

    @abstractmethod
    def is_within_window(
        self,
        timestamp: datetime,
        start: datetime,
        end: datetime,
    ) -> bool:
        """Verifica se um evento pertence a uma janela temporal."""
        ...

    @abstractmethod
    def assert_causality(
        self,
        cause: datetime,
        effect: datetime,
    ) -> None:
        """
        Garante causalidade temporal.
        Levanta erro de domínio se violada.
        """
        ...
```

### Invariantes explícitas (testáveis)

* `earlier <= later`
* `start <= timestamp <= end`
* não existe efeito antes da causa

👉 **Importante**:
o contrato **não diz como medir o tempo**, só **o que é válido**.

---

## 2️⃣ Refinamento do **StatisticalContract**

Esse é o contrato mais crítico do seu sistema.

### Erro comum (que estamos evitando)

Misturar:

* cálculo estatístico
* interpretação científica
* armazenamento

### Refinamento conceitual

No seu domínio:

* Métricas **não são números soltos**
* Toda métrica:

  * tem população
  * tem método
  * tem validade
  * pode ser comparável ou não

### Contrato refinado

```python
from abc import ABC, abstractmethod
from typing import Iterable


class StatisticalContract(ABC):
    """
    Contrato estatístico do domínio.
    Define regras de validade, consistência e comparabilidade de métricas.
    """

    @abstractmethod
    def mean(self, values: Iterable[float]) -> float:
        ...

    @abstractmethod
    def variance(self, values: Iterable[float]) -> float:
        ...

    @abstractmethod
    def is_sample_valid(self, values: Iterable[float]) -> bool:
        """
        Verifica se a amostra atende aos critérios mínimos:
        - tamanho
        - ausência de NaN
        - variância definida
        """
        ...

    @abstractmethod
    def assert_comparable(
        self,
        metric_a: str,
        metric_b: str,
    ) -> None:
        """
        Garante que duas métricas podem ser comparadas cientificamente.
        """
        ...
```

### Invariantes explícitas

* amostras não vazias
* variância definida apenas se `n >= 2`
* métricas só são comparáveis se:

  * mesma unidade
  * mesma janela temporal
  * mesmo método de coleta

👉 Isso protege **pesquisa científica**, não só código.

---

## 3️⃣ Refinamento do **EpistemicContract**

Esse contrato é o que mais diferencia seu sistema de um app comum.

### Refinamento conceitual

Aqui você está dizendo:

> “O sistema não pode fingir que sabe o que não sabe.”

Ou seja:

* inferência ≠ observação
* ausência de dado ≠ dado negativo
* confiança faz parte do conhecimento

### Contrato refinado

```python
from abc import ABC, abstractmethod
from typing import Any


class EpistemicContract(ABC):
    """
    Contrato epistêmico do domínio.
    Define limites do conhecimento, inferência e incerteza.
    """

    @abstractmethod
    def is_observed(self, datum: Any) -> bool:
        ...

    @abstractmethod
    def is_inferred(self, datum: Any) -> bool:
        ...

    @abstractmethod
    def confidence(self, datum: Any) -> float:
        """
        Retorna nível de confiança [0, 1].
        """
        ...

    @abstractmethod
    def assert_known(self, datum: Any) -> None:
        """
        Levanta erro se o dado não for epistemicamente válido.
        """
        ...
```

### Invariantes

* confiança ∈ [0, 1]
* inferido nunca tem confiança máxima
* observado ≠ inferido

---

## 4️⃣ Refinamento do **SoftwareContract**

Esse contrato **protege o domínio contra a infraestrutura**.

### Refinamento conceitual

Aqui você garante:

* determinismo quando exigido
* auditabilidade
* reprodutibilidade

### Contrato refinado

```python
from abc import ABC, abstractmethod


class SoftwareContract(ABC):
    """
    Contrato de software do domínio.
    Define requisitos de segurança, determinismo e auditabilidade.
    """

    @abstractmethod
    def assert_deterministic(self) -> None:
        ...

    @abstractmethod
    def assert_auditable(self) -> None:
        ...

    @abstractmethod
    def assert_versioned(self, version: str) -> None:
        ...
```

---

## 5️⃣ Refinamento final: **Contrato unificado de domínio**

```python
class DomainContract(
    EpistemicContract,
    TemporalContract,
    StatisticalContract,
    SoftwareContract,
):
    """
    Contrato raiz do domínio.
    Nenhuma implementação pode violar estes princípios.
    """
    pass
```

Isso cria um **guardião epistemológico** do sistema.

---

## 🔬 Próximo passo natural (sugestão)

Você agora está pronto para um salto grande:

👉 **Testes baseados em propriedades (property-based testing)**
para validar invariantes estatísticos, temporais e epistêmicos.

Exemplos:

* “nenhuma métrica inválida passa”
* “nenhuma causalidade invertida é aceita”
* “nenhuma inferência vira observação”

Se quiser, o próximo passo pode ser:

> **escrever testes de propriedade com Hypothesis para esses contratos**

Isso elevaria o sistema a **nível de software científico sério**.

Se quiser, seguimos exatamente por aí.
