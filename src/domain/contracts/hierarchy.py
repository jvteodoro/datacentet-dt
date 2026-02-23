"""
Hierarchy Domain Contract — BASELINE v1.0 (REFINED)

Este módulo define as LEIS EMERGENTES do Domain Level.

Ele governa a validade científica de sistemas hierárquicos,
independentemente de escala, tecnologia ou implementação.

Pergunta respondida:
→ "Dado um snapshot hierárquico, a composição continua cientificamente válida?"
"""

from typing import Any, Dict, List

from domain.contracts.temporal import TemporalContract


class HierarchyInvariantViolation(Exception):
    """
    Violação de invariante hierárquico do Domain Level.

    Indica falha emergente do sistema global,
    mesmo quando subsistemas locais são válidos.
    """
    pass


class HierarchyContract:
    """
    Contrato hierárquico do Domain Level.

    Este contrato:
    - é emergente
    - é puro
    - é determinístico
    - opera exclusivamente sobre snapshots hierárquicos
    - não mantém estado
    """

    # ------------------------------------------------------------------
    # Entrada esperada
    # ------------------------------------------------------------------
    # snapshot: Dict[str, Any]
    #
    # Campos semanticamente esperados:
    # - accessed_internal_fields: bool
    # - parent_timestamp: int
    # - child_timestamps: List[int]
    # - parent_variance
    # - child_variances: List[float]
    # - parent_confidence
    # - child_confidences: List[float]
    # - local_error: bool
    # - validated: bool
    # - child_failures: List[bool]
    #
    # O contrato valida RELAÇÕES ENTRE NÍVEIS, não estados isolados.
    # ------------------------------------------------------------------

    def validate(self, snapshot: Dict[str, Any]) -> None:
        """
        Valida o snapshot hierárquico contra os invariantes H1–H4.

        Método:
        - puro
        - determinístico
        - sem efeitos colaterais

        Falha explicitamente com HierarchyInvariantViolation.
        """

        self._validate_H1_encapsulation(snapshot)
        self._validate_H2_temporal_consistency(snapshot)
        self._validate_H3_uncertainty_propagation(snapshot)
        self._validate_H4_error_amplification(snapshot)

    # ------------------------------------------------------------------
    # H1 — Encapsulamento epistêmico hierárquico
    # ------------------------------------------------------------------

    def _validate_H1_encapsulation(self, snapshot: Dict[str, Any]) -> None:
        """
        H1 — Hierarchical Epistemic Encapsulation

        Lei:
        Um nível superior NÃO pode acessar estado interno
        de subsistemas.

        Encapsulamento aqui é epistemológico,
        não técnico.
        """

        if snapshot.get("accessed_internal_fields") is True:
            raise HierarchyInvariantViolation(
                "H1: private/internal state leakage detected"
            )

    # ------------------------------------------------------------------
    # H2 — Consistência temporal hierárquica
    # ------------------------------------------------------------------

    def _validate_H2_temporal_consistency(self, snapshot: Dict[str, Any]) -> None:
        """
        H2 — Hierarchical Temporal Consistency

        Lei:
        Um nível hierárquico superior NÃO pode operar
        epistemicamente antes de seus filhos.
        """

        parent_time = snapshot.get("parent_timestamp")
        child_times: List[int] = snapshot.get("child_timestamps")

        if parent_time is None or child_times is None:
            return

        if any(TemporalContract.is_future(current=parent_time, candidate=t) for t in child_times):
            raise HierarchyInvariantViolation(
                "H2: parent temporal context precedes child context"
            )

    # ------------------------------------------------------------------
    # H3 — Propagação coerente de incerteza
    # ------------------------------------------------------------------

    def _validate_H3_uncertainty_propagation(self, snapshot: Dict[str, Any]) -> None:
        """
        H3 — Coherent Uncertainty Propagation

        Lei:
        Incerteza/confiança do nível superior
        NÃO pode ser mais otimista do que
        a composição admissível dos filhos.
        """

        child_vars = snapshot.get("child_variances")
        parent_var = snapshot.get("parent_variance")

        if parent_var is not None and child_vars is not None:
            if not child_vars:
                raise HierarchyInvariantViolation(
                    "H3: uncertainty propagation requires children"
                )
            if parent_var < min(child_vars):
                raise HierarchyInvariantViolation(
                    "H3: parent uncertainty smaller than children uncertainties"
                )

        child_confs = snapshot.get("child_confidences")
        parent_conf = snapshot.get("parent_confidence")

        if parent_conf is not None and child_confs is not None:
            if not child_confs:
                raise HierarchyInvariantViolation(
                    "H3: confidence propagation requires children"
                )
            if parent_conf > min(child_confs):
                raise HierarchyInvariantViolation(
                    "H3: parent confidence exceeds children confidence bounds"
                )

    # ------------------------------------------------------------------
    # H4 — Não amplificação hierárquica de erro
    # ------------------------------------------------------------------

    def _validate_H4_error_amplification(self, snapshot: Dict[str, Any]) -> None:
        """
        H4 — No Hierarchical Error Amplification

        Lei:
        Erros locais NÃO podem ser promovidos
        ou mascarados como validade global.
        """

        if snapshot.get("local_error") and not snapshot.get("validated"):
            raise HierarchyInvariantViolation(
                "H4: local error promoted without validation"
            )

        child_failures: List[bool] = snapshot.get("child_failures")
        if child_failures is not None:
            if any(child_failures) and all(not f for f in child_failures):
                raise HierarchyInvariantViolation(
                    "H4: child failures masked at parent level"
                )
