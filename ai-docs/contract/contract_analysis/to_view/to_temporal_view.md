Perfeito. Vamos seguir **o mesmo rigor** usado no *software view*, agora para o **Temporal View**.
Sem atalhos, sem “validação escondida”, sem misturar responsabilidades.

Vou manter a mesma estrutura:

1️⃣ O que é o *Temporal View*
2️⃣ O que o **TemporalContract realmente valida**
3️⃣ Campos necessários e origem no Snapshot
4️⃣ Forma canônica do `temporal_view`
5️⃣ Implementação correta de `to_temporal_view()`
6️⃣ Observações críticas de arquitetura

---

## 1️⃣ O que é o Temporal View

O **Temporal View** é:

> Uma **projeção causal-temporal** de um snapshot, usada **exclusivamente** para validar os invariantes temporais T1–T4.

Ele **não**:

* ❌ implementa relógio
* ❌ compara snapshots entre si
* ❌ mantém histórico
* ❌ aplica janelas, tolerâncias ou sincronização

Ele responde **uma única pergunta**:

> “Este snapshot é temporalmente e causalmente admissível?”

---

## 2️⃣ O que o TemporalContract valida (escopo real)

Relembrando o contrato **refinado** que você congelou:

### Invariantes cobertos

* **T1** — existência de timestamp
* **T2** — monotonicidade (via `previous_timestamp`)
* **T3** — causalidade (inputs não vêm do futuro)
* **T4** — alinhamento explícito (estado vs observação)

⚠️ Importante:
O contrato **não sabe**:

* de onde vêm os timestamps
* se são sensores, estados ou inferências
* como o snapshot foi produzido

Ele só valida **relações temporais declaradas**.

---

## 3️⃣ Campos exigidos pelo TemporalContract

Do contrato:

```text
Campos semanticamente esperados:
- timestamp: int
- previous_timestamp: Optional[int]
- input_timestamps: Optional[List[int]]
- state_timestamp: Optional[int]
- observation_timestamp: Optional[int]
```

Agora precisamos mapear **exatamente** isso ao Snapshot.

---

## 4️⃣ Origem de cada campo no Snapshot

### 🔹 `timestamp`

* Timestamp lógico do snapshot
* **Já existe** no Snapshot

```python
snapshot.timestamp
```

---

### 🔹 `previous_timestamp`

* Timestamp do snapshot anterior na **mesma linha causal**
* ⚠️ O Snapshot **não deve inferir isso**
* Deve ser:

  * passado explicitamente
  * ou `None`

➡️ Deve existir como **metadado opcional do Snapshot**

---

### 🔹 `input_timestamps`

* Timestamps das entidades que alimentaram este snapshot
* Exemplos:

  * observáveis usados
  * estados filhos
  * medições combinadas

➡️ Pode ser derivado de:

* `Observable.timestamp`
* `Identifiable.timestamp`
* snapshots filhos (no futuro)

Mas o **Snapshot deve carregar o resultado**, não o processo.

---

### 🔹 `state_timestamp`

* Timestamp do estado interno (se existir)

Origem:

```python
snapshot.state_vector.timestamp
```

(se `state_vector` existir)

---

### 🔹 `observation_timestamp`

* Timestamp das observações combinadas

Regra simples e segura:

* Se houver observáveis → todos já compartilham timestamp (SN2)
* Então podemos usar:

```python
snapshot.observables[0].timestamp
```

(se houver observáveis)

---

## 5️⃣ Forma canônica do Temporal View

Exatamente isto, nada além:

```python
{
    "timestamp": int,
    "previous_timestamp": Optional[int],
    "input_timestamps": List[int],
    "state_timestamp": Optional[int],
    "observation_timestamp": Optional[int],
}
```

⚠️ Mesmo se listas estiverem vazias, elas devem existir como listas.

---

## 6️⃣ Implementação: `to_temporal_view()`

```python
class Snapshot:
    ...
    def to_temporal_view(self) -> Dict[str, Any]:
        """
        Temporal View — Causal Projection

        Projeta o snapshot para validação do Temporal Domain Contract.

        Esta view:
        - é pura
        - é determinística
        - não infere causalidade
        - apenas declara relações temporais explícitas
        """

        # Timestamp principal do snapshot
        timestamp = self._timestamp

        # Timestamp do estado (se existir)
        state_timestamp = (
            self._state_vector.timestamp
            if self._state_vector is not None
            else None
        )

        # Timestamp das observações (se existirem)
        observation_timestamp = (
            self._observables[0].timestamp
            if self._observables
            else None
        )

        # Inputs causais explícitos
        input_timestamps = []

        if self._observables:
            input_timestamps.extend(o.timestamp for o in self._observables)

        if self._parameters:
            input_timestamps.extend(p.timestamp for p in self._parameters)

        return {
            "timestamp": timestamp,
            "previous_timestamp": self._previous_timestamp,
            "input_timestamps": list(input_timestamps),
            "state_timestamp": state_timestamp,
            "observation_timestamp": observation_timestamp,
        }
```

---

## 7️⃣ Observações críticas (muito importantes)

### 🔴 O Snapshot NÃO:

* compara timestamps
* decide causalidade
* valida alinhamento

Ele **apenas declara**.

---

### 🔴 O Validator NÃO:

* acessa objetos vivos
* infere timestamps
* mexe em estado

Ele apenas faz:

```python
TemporalContract().validate(snapshot.to_temporal_view())
```

---

## 8️⃣ Checklist de sanidade arquitetural

✔️ Contrato continua puro
✔️ Snapshot continua imutável
✔️ Validação não é duplicada
✔️ Nenhuma regra temporal está “espalhada”
✔️ Pronto para hierarquia futura

---

## Próximo passo natural

👉 **Derivar `to_statistical_view()`**, que é mais sutil (porque mistura variância, covariância e composição).

Quando quiser, seguimos.
