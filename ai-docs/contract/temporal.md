Perfeito. Vamos para o **contrato temporal**, mantendo o mesmo **nível profissional**, **rigor de controle** e **Design by Contract**.

---

# 2️⃣ `domain/contracts/temporal.py`

## 1. Motivação teórica (por que o contrato temporal existe)

Em teoria de controle **tempo não é detalhe**, é estrutura:

* Estados só fazem sentido **em um instante**
* Observações chegam **com atraso**
* Estimativas são feitas **em janelas**
* Sistemas hierárquicos operam em **diferentes escalas temporais**

Em um Digital Twin hierárquico de data center:

* Sensores → ms / s
* Subsistemas → s / min
* Orquestração global → min / horas

👉 O **contrato temporal** garante que:

> **nenhuma inferência viole causalidade, ordem temporal ou coerência de relógio**

Sem isso:

* filtros quebram
* identificação fica inválida
* controle vira superstição

---

## 2. Responsabilidades do contrato temporal

O contrato temporal define:

### 🔹 Causalidade

* Nada do futuro pode afetar o passado
* Estado em ( t ) só depende de ( \le t )

### 🔹 Ordenação

* Observações têm timestamp consistente
* Estados têm timestamp associado

### 🔹 Sincronização

* Diferença aceitável entre relógios
* Alinhamento entre níveis hierárquicos

### 🔹 Janelas temporais

* Tamanho mínimo para estimativa
* Tamanho máximo antes de obsolescência

---

## 3. Decisões de design

### ✔️ Tempo explícito

* Nunca implícito
* Nada de `now()` escondido

### ✔️ Independente de relógio físico

* Pode ser:

  * tempo real
  * tempo lógico
  * tempo de simulação

### ✔️ Determinístico

* Mesma sequência → mesmo resultado

---

## 4. Interface formal (Design by Contract)

```python
# domain/contracts/temporal.py

from abc import ABC, abstractmethod
from typing import Any
from datetime import timedelta


class TemporalViolation(Exception):
    """Raised when temporal assumptions are violated."""
    pass


class TemporalContract(ABC):
    """
    Temporal contract defines causal and timing guarantees
    of the Digital Twin.
    """

    # ----------------------------
    # Timestamps
    # ----------------------------
    @abstractmethod
    def validate_timestamp(self, timestamp: float) -> None:
        """
        Validates whether a timestamp is admissible.

        Preconditions:
        - Timestamp must be finite
        - Timestamp must be non-negative

        Raises:
            TemporalViolation
        """
        raise NotImplementedError

    # ----------------------------
    # Ordering
    # ----------------------------
    @abstractmethod
    def validate_ordering(self, previous_ts: float, current_ts: float) -> None:
        """
        Ensures temporal ordering.

        Preconditions:
        - current_ts >= previous_ts

        Raises:
            TemporalViolation
        """
        raise NotImplementedError

    # ----------------------------
    # Latency
    # ----------------------------
    @abstractmethod
    def max_latency(self) -> timedelta:
        """
        Maximum admissible observation or actuation latency.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_latency(self, event_ts: float, received_ts: float) -> None:
        """
        Validates whether latency is acceptable.

        Raises:
            TemporalViolation
        """
        raise NotImplementedError

    # ----------------------------
    # Sampling
    # ----------------------------
    @abstractmethod
    def sampling_period(self) -> timedelta:
        """
        Nominal sampling period of the system.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_sampling(self, delta_t: timedelta) -> None:
        """
        Validates whether sampling interval is admissible.

        Raises:
            TemporalViolation
        """
        raise NotImplementedError

    # ----------------------------
    # Windowing
    # ----------------------------
    @abstractmethod
    def min_window_size(self) -> int:
        """
        Minimum number of samples required for estimation.
        """
        raise NotImplementedError

    @abstractmethod
    def max_window_age(self) -> timedelta:
        """
        Maximum age of data before it becomes stale.
        """
        raise NotImplementedError
```

---

## 5. Invariantes temporais fundamentais

### ⏱️ Invariante de Causalidade

> Nenhum estado pode depender de observações futuras.

### ⏱️ Invariante de Monotonicidade

> Timestamps são não decrescentes.

### ⏱️ Invariante de Frescor

> Dados antigos demais **não** alimentam inferência.

### ⏱️ Invariante Hierárquico

> Níveis superiores operam em escalas temporais maiores
> ou iguais às dos níveis inferiores.

---

## 6. Como isso se conecta aos outros contratos

| Contrato    | Relação                                      |
| ----------- | -------------------------------------------- |
| Epistêmico  | Tempo inválido → conhecimento inválido       |
| Estatístico | Janela temporal define validade estatística  |
| Software    | Garante consistência de chamadas assíncronas |

---

## 7. Exemplo conceitual rápido

* Sensor mede tensão às 10:00:00
* Chega ao DT às 10:00:05
* `max_latency = 2s`

👉 Violação temporal → dado descartado
Mesmo que o valor elétrico esteja “perfeito”

---

## 8. Checklist de maturidade

✔️ Compatível com Kalman / filtros Bayesianos
✔️ Compatível com aprendizado online
✔️ Compatível com hierarquia
✔️ Compatível com simulação
✔️ Compatível com replay histórico

---

### Próximo contrato

👉 **`statistical.py`**

* incerteza
* confiança
* covariância
* validade estatística

Quando quiser, diga: **“vamos para o estatístico”**
