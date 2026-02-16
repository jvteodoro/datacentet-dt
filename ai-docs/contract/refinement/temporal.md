Excelente, vamos manter **o mesmo nível profissional** e a **mesma filosofia de contrato executável** que usamos no contrato estatístico.

Aqui o **TemporalContract** é ainda mais crítico, porque ele:

* garante **coerência dinâmica**
* protege o sistema contra *time leaks*, *state jumps* e *causalidade quebrada*
* é o que permite **hierarquia de Digital Twins** funcionar corretamente

Vou apresentar o código **com comentários extensivos**, focado para que:

* você saiba exatamente **o que cada método deve garantir**
* o contrato seja independente de implementação (discreto, contínuo, híbrido, event-driven)

---

# `domain/contracts/temporal.py` — versão refinada e comentada

```python
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime, timedelta


class TemporalViolation(Exception):
    """
    Raised when temporal assumptions, ordering, causality or
    synchronization constraints are violated.

    This represents a *domain-level* temporal inconsistency, not a
    scheduling or runtime error.
    """
    pass


class TemporalContract(ABC):
    """
    TemporalContract defines the rules governing time, ordering,
    causality and temporal coherence inside the Digital Twin.

    This contract is fundamental for:
    - state estimation
    - hierarchical composition
    - multi-rate systems
    - delayed or asynchronous measurements

    The contract does NOT enforce:
    - real-time execution
    - specific clocks
    - specific sampling rates

    Instead, it enforces *logical temporal consistency*.
    """

    # ==========================================================
    # Time Representation
    # ==========================================================

    @abstractmethod
    def current_time(self) -> datetime:
        """
        Returns the current logical time of the component.

        This is NOT necessarily wall-clock time.
        It represents the *epistemic time* at which the current state
        estimate is valid.

        Invariants:
        - Time must be monotonically non-decreasing
        - Returned time must be comparable with past timestamps

        Returns:
            datetime:
                Logical time associated with the current state.
        """
        raise NotImplementedError

    @abstractmethod
    def last_update_time(self) -> Optional[datetime]:
        """
        Returns the logical time of the last successful state update.

        This method allows higher layers to reason about:
        - staleness
        - latency
        - synchronization across subsystems

        Returns:
            datetime or None:
                None indicates that no update has occurred yet.
        """
        raise NotImplementedError

    # ==========================================================
    # Temporal Ordering and Causality
    # ==========================================================

    @abstractmethod
    def validate_time_order(
        self,
        previous_time: datetime,
        new_time: datetime,
    ) -> None:
        """
        Validates that `new_time` respects temporal ordering relative
        to `previous_time`.

        This method enforces causality: effects cannot precede causes.

        Preconditions:
        - Both timestamps are expressed in the same logical time domain

        Postconditions:
        - new_time >= previous_time

        Raises:
            TemporalViolation:
                If time moves backwards or violates ordering constraints.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_update_causality(
        self,
        state_time: datetime,
        measurement_time: datetime,
    ) -> None:
        """
        Validates that a measurement or input can legitimately affect
        a state estimate at `state_time`.

        This is crucial for:
        - delayed measurements
        - out-of-order data
        - buffering and smoothing

        Typical admissible cases:
        - measurement_time <= state_time
        - bounded-lag smoothing policies

        Raises:
            TemporalViolation:
                If causality is violated beyond admissible policy.
        """
        raise NotImplementedError

    # ==========================================================
    # Time Step and Dynamics
    # ==========================================================

    @abstractmethod
    def delta_t(
        self,
        previous_time: datetime,
        new_time: datetime,
    ) -> timedelta:
        """
        Computes the logical time difference between two timestamps.

        This value is used by:
        - dynamic models
        - state propagation
        - numerical integration

        Preconditions:
        - validate_time_order(previous_time, new_time) has succeeded

        Postconditions:
        - Returned timedelta is non-negative

        Returns:
            timedelta:
                Logical elapsed time.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_delta_t(self, delta_t: timedelta) -> None:
        """
        Validates whether a time step is admissible for the system.

        This allows enforcing:
        - maximum step sizes (numerical stability)
        - minimum step sizes (noise dominance)
        - zero-step handling policies

        Raises:
            TemporalViolation:
                If delta_t is outside admissible bounds.
        """
        raise NotImplementedError

    # ==========================================================
    # Update Semantics
    # ==========================================================

    @abstractmethod
    def validate_update_sequence(
        self,
        previous_state: Any,
        new_state: Any,
        previous_time: datetime,
        new_time: datetime,
    ) -> None:
        """
        Validates whether a transition from `previous_state` to
        `new_state` between `previous_time` and `new_time` is
        temporally admissible.

        This method enforces:
        - no state jumps without time elapsing
        - no multiple conflicting updates at the same time
        - temporal coherence of hierarchical updates

        Preconditions:
        - previous_state is valid at previous_time

        Postconditions:
        - new_state is valid at new_time

        Raises:
            TemporalViolation:
                If the update violates temporal semantics.
        """
        raise NotImplementedError

    # ==========================================================
    # Staleness and Freshness
    # ==========================================================

    @abstractmethod
    def max_staleness(self) -> timedelta:
        """
        Returns the maximum admissible staleness of the state estimate.

        This is a policy-level parameter used by:
        - orchestrators
        - hierarchical Digital Twins
        - controllers

        Returns:
            timedelta:
                Maximum allowed age of the state estimate.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_freshness(self) -> None:
        """
        Validates whether the current state estimate is sufficiently
        fresh relative to the current logical time.

        Preconditions:
        - current_time() is defined
        - last_update_time() is defined

        Raises:
            TemporalViolation:
                If the state estimate is stale beyond admissible bounds.
        """
        raise NotImplementedError
```

---

# 🧠 O que este contrato garante no seu Digital Twin

Com esse contrato, você **formaliza cientificamente**:

### ✔ Causalidade

Nada “vem do futuro” sem uma política explícita (ex: smoothing).

### ✔ Hierarquia segura

Níveis superiores podem confiar que:

* estados não “pulam”
* tempos são coerentes
* staleness é explícito

### ✔ Independência de implementação

Funciona para:

* sistemas discretos
* contínuos
* híbridos
* event-driven
* data-driven

---

# Conexão com os outros contratos

| Contrato     | Pergunta que responde   |
| ------------ | ----------------------- |
| Epistemic    | *O que sabemos?*        |
| **Temporal** | *Quando isso é válido?* |
| Statistical  | *Quão confiável é?*     |
| Software     | *Como isso se conecta?* |

---

## Próximo passo natural

Podemos agora:

1. Refinar **invariantes temporais globais**
2. Definir **testes de propriedade (Hypothesis)** para tempo
3. Integrar o TemporalContract na **DomainLevel interface**
4. Criar um **fake temporal policy** para TDD

Quando quiser, seguimos exatamente nessa ordem.
