Excelente. O **contrato estatístico** é onde o Digital Twin deixa de ser apenas “bem organizado” e passa a ser **cientificamente defensável**. Vamos tratá-lo com o mesmo rigor.

---

# 3️⃣ `domain/contracts/statistical.py`

## 1. Motivação teórica (por que o contrato estatístico existe)

Em controle, identificação e Digital Twins:

* **Não existem medições perfeitas**
* **Não existem estados exatos**
* **Toda inferência carrega incerteza**

O erro clássico em sistemas de DT é:

> tratar estimativas como valores determinísticos

O **contrato estatístico** impede isso ao definir:

> **quais distribuições são assumidas,
> como a incerteza é representada,
> e quando uma estimativa é estatisticamente válida**

Sem esse contrato:

* filtros parecem funcionar, mas divergem
* identificadores aprendem ruído
* decisões são tomadas com falsa confiança

---

## 2. Responsabilidades do contrato estatístico

O contrato estatístico define:

### 🔹 Representação da incerteza

* Covariância
* Variância
* Intervalos de confiança
* Distribuições

### 🔹 Qualidade estatística

* Confiança mínima
* Consistência numérica
* Estabilidade estatística

### 🔹 Compatibilidade entre módulos

* Estado ↔ observações
* Estado ↔ parâmetros
* Modelo físico ↔ modelo estatístico

---

## 3. Decisões de design

### ✔️ Distribuição explícita

Nada de “float solto”.

### ✔️ Modelo-agnóstico

* Gaussiano
* Não-gaussiano
* Amostral (particle filters)
* Bayesian neural nets

### ✔️ Separação clara

* Estatística ≠ epistemologia
* Estatística ≠ tempo

---

## 4. Interface formal (Design by Contract)

```python
# domain/contracts/statistical.py

from abc import ABC, abstractmethod
from typing import Any, Optional
import numpy as np


class StatisticalViolation(Exception):
    """Raised when statistical assumptions are violated."""
    pass


class StatisticalContract(ABC):
    """
    Statistical contract defines how uncertainty is represented,
    propagated and validated within the Digital Twin.
    """

    # ----------------------------
    # Uncertainty representation
    # ----------------------------
    @abstractmethod
    def validate_distribution(self, value: Any) -> None:
        """
        Validates whether a value has a valid statistical representation.

        Preconditions:
        - Distribution must be well-defined
        - Parameters must be finite

        Raises:
            StatisticalViolation
        """
        raise NotImplementedError

    @abstractmethod
    def covariance(self, value: Any) -> np.ndarray:
        """
        Returns covariance matrix associated with value.

        Postconditions:
        - Covariance is symmetric
        - Covariance is positive semi-definite
        """
        raise NotImplementedError

    # ----------------------------
    # Confidence
    # ----------------------------
    @abstractmethod
    def confidence(self, value: Any) -> float:
        """
        Returns confidence level associated with value.

        Returns:
            float in (0, 1]
        """
        raise NotImplementedError

    @abstractmethod
    def min_confidence(self) -> float:
        """
        Minimum statistically admissible confidence.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_confidence(self, value: Any) -> None:
        """
        Ensures confidence is acceptable.

        Raises:
            StatisticalViolation
        """
        raise NotImplementedError

    # ----------------------------
    # Consistency
    # ----------------------------
    @abstractmethod
    def validate_consistency(
        self,
        predicted: Any,
        observed: Any,
    ) -> None:
        """
        Validates statistical consistency between prediction and observation.

        Typical checks:
        - Innovation within bounds
        - Normalized residual tests

        Raises:
            StatisticalViolation
        """
        raise NotImplementedError
```

---

## 5. Invariantes estatísticos fundamentais

### 📊 Invariante de Incerteza

> Toda estimativa carrega incerteza explícita.

### 📊 Invariante de Confiança

> Estimativas abaixo da confiança mínima
> **não podem** ser propagadas.

### 📊 Invariante de Consistência

> Observações inconsistentes com o estado
> devem ser rejeitadas ou penalizadas.

---

## 6. Como isso se conecta com filtros e identificação

| Componente      | Uso do contrato           |
| --------------- | ------------------------- |
| Kalman / EKF    | Covariância, inovação     |
| UKF             | Consistência estatística  |
| Particle Filter | Amostras + peso           |
| Identificação   | Confiança do parâmetro    |
| Controle        | Penalização por incerteza |

---

## 7. Exemplo conceitual

* Estado estimado:

  * ( \hat{x} = 230V )
  * ( \sigma = 20V )
  * Confiança = 0.6
* `min_confidence = 0.8`

👉 Estado **não** pode subir de nível hierárquico
Mesmo sendo “numericamente razoável”

---

## 8. Checklist de maturidade

✔️ Compatível com controle estocástico
✔️ Compatível com aprendizado online
✔️ Compatível com modelos físicos e ML
✔️ Compatível com validação científica
✔️ Compatível com auditoria de decisões

---

### Próximo contrato

👉 **`software.py`**

* acoplamento
* dependências
* versionamento
* compatibilidade hierárquica
* LSP / ISP

Quando quiser, diga: **“vamos para o software”**
