Perfeito. Vamos para **ETAPA 2 — E1 (Invariante Epistêmica)** com o **mesmo rigor** usado em SW1, T1 e S1.

Vou seguir exatamente o padrão que consolidamos:

1. Relembrar **o que é E1**
2. Definir **escopo do teste**
3. Escrever **testes TDD (pytest)**
4. Explicar **o porquê de cada teste**
5. Deixar claro **o que o contrato deverá implementar depois**

Sem pular nada.

---

# 🔒 E1 — Invariante Epistêmica Fundamental

## Definição (nível conceitual)

> **E1**: *Toda métrica, estado ou decisão no sistema deve ser epistemicamente justificável.*

Ou seja:

* Nenhum valor “aparece do nada”
* Todo dado deve ter:

  * origem
  * método de obtenção
  * nível de confiança
* O sistema **não pode usar** dados sem lastro epistêmico

---

## Tradução operacional de E1

Para o sistema de Digital Twins / Training / Research:

Um **EpistemicRecord** válido deve:

1. Ter uma **fonte explícita**
2. Ter um **método de obtenção**
3. Ter um **nível de confiança válido**
4. Permitir **auditoria da justificativa**
5. Ser possível responder: *“por que esse valor existe?”*

---

# 📐 Escopo do TDD (ETAPA 2)

Vamos testar **apenas a invariante**, não a implementação.

O contrato epistêmico já define (ou definirá) algo como:

```python
EpistemicRecord
EpistemicJustification
EpistemicConfidence
```

Os testes irão assumir **interfaces mínimas**, mesmo que o código ainda não exista.

---

# 🧪 Arquivo de Teste

📁 `tests/domain/contracts/test_epistemic_E1.py`

---

## 🧪 Teste 1 — Um registro sem fonte viola E1

```python
import pytest

from domain.contracts.epistemic import EpistemicRecord, EpistemicViolation
```

```python
def test_E1_record_without_source_is_invalid():
    record = EpistemicRecord(
        value=120,
        source=None,                     # ❌ sem fonte
        method="sensor_reading",
        confidence=0.9,
        justification="Heart rate sensor"
    )

    with pytest.raises(EpistemicViolation):
        record.validate_epistemic_integrity()
```

### O que este teste garante

✔ O sistema **não aceita dados órfãos**
✔ Fonte é **obrigatória**, não opcional
✔ Erro explícito (não silencioso)

---

## 🧪 Teste 2 — Um registro sem método viola E1

```python
def test_E1_record_without_method_is_invalid():
    record = EpistemicRecord(
        value=85,
        source="Polar H10",
        method=None,                     # ❌ método ausente
        confidence=0.95,
        justification="Chest strap HR"
    )

    with pytest.raises(EpistemicViolation):
        record.validate_epistemic_integrity()
```

### Garantia

✔ O sistema exige **como** o dado foi produzido
✔ Diferencia *origem* de *processo*

---

## 🧪 Teste 3 — Confiança fora do intervalo viola E1

```python
@pytest.mark.parametrize("confidence", [-0.1, 0, 1.1, 2])
def test_E1_invalid_confidence_levels(confidence):
    record = EpistemicRecord(
        value=200,
        source="Force Plate",
        method="average_peak_force",
        confidence=confidence,           # ❌ inválido
        justification="Lab measurement"
    )

    with pytest.raises(EpistemicViolation):
        record.validate_epistemic_integrity()
```

### Garantia

✔ Confiança é **normalizada**
✔ Evita falsos absolutos ou nonsense estatístico
✔ Base para integração com S1 depois

---

## 🧪 Teste 4 — Justificativa vazia viola E1

```python
def test_E1_record_without_justification_is_invalid():
    record = EpistemicRecord(
        value=42,
        source="Coach input",
        method="subjective_rating",
        confidence=0.6,
        justification=""                 # ❌ vazio
    )

    with pytest.raises(EpistemicViolation):
        record.validate_epistemic_integrity()
```

### Garantia

✔ Sempre existe uma **narrativa explicável**
✔ Essencial para auditoria, pesquisa e revisão humana

---

## 🧪 Teste 5 — Registro completo satisfaz E1

```python
def test_E1_valid_epistemic_record_passes():
    record = EpistemicRecord(
        value=1.85,
        source="IMU Sensor",
        method="computed_stride_length",
        confidence=0.92,
        justification="Kalman filtered stride estimation"
    )

    # Não deve lançar exceção
    record.validate_epistemic_integrity()
```

### Garantia

✔ Caminho feliz explícito
✔ Define o **contrato de validade mínima**

---

# 🧠 O que o contrato Epistêmico PRECISA implementar depois

Para que esses testes passem, o contrato deverá:

```python
class EpistemicRecord(Protocol):
    value: Any
    source: str
    method: str
    confidence: float
    justification: str

    def validate_epistemic_integrity(self) -> None:
        """
        Raises EpistemicViolation if any epistemic invariant is violated.
        """
```

E uma exceção explícita:

```python
class EpistemicViolation(Exception):
    ...
```

---

# 📌 Estado atual da ETAPA 2

| Invariante | Status                |
| ---------- | --------------------- |
| SW1        | ✅ Finalizado          |
| T1         | ✅ Refinado            |
| S1         | ✅ Implementado        |
| **E1**     | ✅ **Testes escritos** |

---

## Próximo passo (quando você disser)

👉 **“Vamos para E2”**
Ou, se preferir:

👉 **“Refinar E1”** (edge cases, composição com T1/S1)

Seguimos no mesmo nível de precisão.
