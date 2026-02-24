"""
Temporal Domain Contract — BASELINE v1.0 (REFINED)

Este módulo define as LEIS TEMPORAIS do Domain Level.

Ele NÃO:
- implementa relógios físicos
- sincroniza tempo
- mantém estado
- impõe janelas ou tolerâncias

Pergunta respondida:
→ "Dado um snapshot, a linha do tempo utilizada é causalmente válida?"
"""

from typing import Any, Dict, List


class TemporalViolation(Exception):
    """
    Violação de contrato temporal do Domain Level.

    Indica quebra de causalidade, ordenação ou coerência temporal.
    Nunca representa erro técnico ou de infraestrutura.
    """
    pass


class TemporalContract:
    """
    Contrato temporal do Domain Level.

    Este contrato:
    - é puro
    - é determinístico
    - opera apenas sobre snapshots
    - não mantém memória entre validações
    """

    # ------------------------------------------------------------------
    # Entrada esperada
    # ------------------------------------------------------------------
    # snapshot: Dict[str, Any]
    #
    # Campos semanticamente esperados:
    # - timestamp: int
    # - previous_timestamp: Optional[int]
    # - input_timestamps: Optional[List[int]]
    #
    # O contrato NÃO assume como esses dados são produzidos.
    # ------------------------------------------------------------------

    def validate(self, snapshot: Dict[str, Any]) -> None:
        """
        Valida o snapshot contra os invariantes temporais T1–T4.

        Método:
        - puro
        - determinístico
        - sem efeitos colaterais

        Falha explicitamente com TemporalViolation.
        """

        self._validate_T1_context(snapshot)
        self._validate_T2_monotonicity(snapshot)
        self._validate_T3_causality(snapshot)
        self._validate_T4_alignment(snapshot)

    @staticmethod
    def is_future(*, current: int, candidate: int) -> bool:
        """
        Regra temporal canônica:
        candidate > current caracteriza dado do futuro.

        Igualdade (candidate == current) é admissível.
        """

        return candidate > current

    @classmethod
    def ensure_non_regressive(cls, *, previous: int, current: int, code: str) -> None:
        """Valida monotonicidade canônica: current >= previous."""

        if cls.is_future(current=current, candidate=previous):
            raise TemporalViolation(f"{code}: temporal regression detected")

    @classmethod
    def ensure_not_future(cls, *, current: int, candidate: int, code: str) -> None:
        """Valida causalidade canônica: candidate <= current."""

        if cls.is_future(current=current, candidate=candidate):
            raise TemporalViolation(f"{code}: future data is not causally admissible")

    # ------------------------------------------------------------------
    # T1 — Existência de contexto temporal válido
    # ------------------------------------------------------------------

    def _validate_T1_context(self, snapshot: Dict[str, Any]) -> None:
        """
        T1 — Temporal Context Existence

        Lei:
        Nenhuma entidade epistemicamente válida pode existir
        fora de um contexto temporal explícito.

        Falhas cobertas:
        - ausência de timestamp
        - tipo inválido
        """

        timestamp = snapshot.get("timestamp")

        if timestamp is None:
            raise TemporalViolation("T1: missing timestamp")

        if not isinstance(timestamp, int):
            raise TemporalViolation("T1: timestamp must be an integer domain value")

    # ------------------------------------------------------------------
    # T2 — Monotonicidade temporal
    # ------------------------------------------------------------------

    def _validate_T2_monotonicity(self, snapshot: Dict[str, Any]) -> None:
        """
        T2 — Temporal Monotonicity

        Lei:
        O tempo não pode regredir dentro de uma mesma linha causal.

        Falhas cobertas:
        - regressão temporal
        """

        previous = snapshot.get("previous_timestamp")
        current = snapshot.get("timestamp")

        if previous is None:
            # Primeira ocorrência na linha causal
            return

        if not isinstance(previous, int):
            raise TemporalViolation("T2: previous_timestamp must be integer")

        self.ensure_non_regressive(previous=previous, current=current, code="T2")

    # ------------------------------------------------------------------
    # T3 — Causalidade temporal
    # ------------------------------------------------------------------

    def _validate_T3_causality(self, snapshot: Dict[str, Any]) -> None:
        """
        T3 — Temporal Causality

        Lei:
        Nenhuma inferência ou atualização pode utilizar
        dados provenientes do futuro.

        Falhas cobertas:
        - uso de dados futuros
        """

        now = snapshot.get("timestamp")
        inputs: List[int] = snapshot.get("input_timestamps", [])

        if not inputs:
            return

        for t in inputs:
            if not isinstance(t, int):
                raise TemporalViolation("T3: input timestamp must be integer")

            if t >= now:
                raise TemporalViolation("T3: future data is not causally admissible")

    # ------------------------------------------------------------------
    # T4 — Alinhamento temporal
    # ------------------------------------------------------------------

    def _validate_T4_alignment(self, snapshot: Dict[str, Any]) -> None:
        """
        T4 — Temporal Alignment

        Lei:
        Dados combinados devem pertencer a contextos temporais
        explicitamente compatíveis.

        Este contrato exige alinhamento EXPLÍCITO.
        Nenhuma tolerância é assumida.

        Falhas cobertas:
        - fusão de dados defasados
        """

        state_time = snapshot.get("state_timestamp")
        observation_time = snapshot.get("observation_timestamp")

        if state_time is None or observation_time is None:
            # Alinhamento não aplicável neste snapshot
            return

        if state_time != observation_time:
            raise TemporalViolation("T4: temporal misalignment detected")
