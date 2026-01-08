"""
Epistemic Domain Contract — BASELINE v1.0 (REFINED)

Este módulo define as LEIS EPISTÊMICAS do Domain Level.

Ele NÃO:
- implementa inferência
- armazena conhecimento
- calcula estatística
- define modelos físicos

Pergunta respondida:
→ "Dado um snapshot, aquilo que está sendo declarado
   como conhecimento é cientificamente válido?"
"""

from typing import Any, Dict, List


class EpistemicViolation(Exception):
    """
    Violação de contrato epistêmico do Domain Level.

    Indica inconsistência científica, semântica
    ou epistemológica no conhecimento declarado.
    """
    pass


class EpistemicContract:
    """
    Contrato epistêmico do Domain Level.

    Este contrato:
    - é puro
    - é determinístico
    - opera exclusivamente sobre snapshots
    - não mantém estado
    """

    # ------------------------------------------------------------------
    # Entrada esperada
    # ------------------------------------------------------------------
    # snapshot: Dict[str, Any]
    #
    # Campos semanticamente esperados:
    # - value
    # - source: str
    # - method: str
    # - justification: str
    # - confidence: float
    # - epistemic_type: str  ("observed", "inferred", "assumed", ...)
    # - child_confidences: Optional[List[float]]
    #
    # O contrato valida LEIS epistêmicas, não formatos rígidos.
    # ------------------------------------------------------------------

    def validate(self, snapshot: Dict[str, Any]) -> None:
        """
        Valida o snapshot contra os invariantes epistêmicos E1–E5.

        Método:
        - puro
        - determinístico
        - sem efeitos colaterais

        Falha explicitamente com EpistemicViolation.
        """

        self._validate_E1_integrity(snapshot)
        self._validate_E2_uncertainty(snapshot)
        self._validate_E3_fact_vs_inference(snapshot)
        self._validate_E4_composition(snapshot)
        self._validate_E5_auditability(snapshot)

    # ------------------------------------------------------------------
    # E1 — Integridade epistêmica
    # ------------------------------------------------------------------

    def _validate_E1_integrity(self, snapshot: Dict[str, Any]) -> None:
        """
        E1 — Epistemic Integrity

        Lei:
        Todo conhecimento declarado deve possuir:
        - origem (source)
        - método
        - justificativa explícita

        Falhas cobertas:
        - origem desconhecida
        - conhecimento não justificável
        """

        for field in ("source", "method", "justification"):
            value = snapshot.get(field)
            if not isinstance(value, str) or not value.strip():
                raise EpistemicViolation(
                    f"E1: missing or invalid epistemic field '{field}'"
                )

    # ------------------------------------------------------------------
    # E2 — Incerteza epistêmica explícita
    # ------------------------------------------------------------------

    def _validate_E2_uncertainty(self, snapshot: Dict[str, Any]) -> None:
        """
        E2 — Explicit Epistemic Uncertainty

        Lei:
        Limites de conhecimento devem ser explicitados.

        Confiança:
        - não é verdade
        - não é estatística
        - é um limite epistêmico
        """

        confidence = snapshot.get("confidence")

        if confidence is None:
            raise EpistemicViolation("E2: epistemic confidence must be explicit")

        if not isinstance(confidence, (int, float)):
            raise EpistemicViolation("E2: confidence must be numeric")

        if not (0 < confidence <= 1):
            raise EpistemicViolation("E2: confidence must be in (0, 1]")

    # ------------------------------------------------------------------
    # E3 — Separação fato vs inferência
    # ------------------------------------------------------------------

    def _validate_E3_fact_vs_inference(self, snapshot: Dict[str, Any]) -> None:
        """
        E3 — Fact vs Inference Separation

        Lei lógica:
        Inferência NÃO é fato.

        Um snapshot NÃO pode simultaneamente:
        - declarar-se inferido
        - declarar-se fato estabilizado
        """

        epistemic_type = snapshot.get("epistemic_type")

        if epistemic_type is None:
            return

        if epistemic_type == "inferred" and snapshot.get("is_fact") is True:
            raise EpistemicViolation(
                "E3: inferred knowledge cannot be treated as fact"
            )

    # ------------------------------------------------------------------
    # E4 — Composição epistêmica segura
    # ------------------------------------------------------------------

    def _validate_E4_composition(self, snapshot: Dict[str, Any]) -> None:
        """
        E4 — Safe Epistemic Composition

        Lei:
        Conhecimento composto NÃO pode ser epistemicamente
        mais forte do que suas fontes.

        Esta é uma lei de prudência científica.
        """

        parent_conf = snapshot.get("confidence")
        child_confs: List[float] = snapshot.get("child_confidences")

        if child_confs is None:
            return

        if not child_confs:
            raise EpistemicViolation("E4: epistemic composition requires children")

        if parent_conf > min(child_confs):
            raise EpistemicViolation(
                "E4: parent confidence cannot exceed weakest child confidence"
            )

    # ------------------------------------------------------------------
    # E5 — Auditabilidade científica
    # ------------------------------------------------------------------

    def _validate_E5_auditability(self, snapshot: Dict[str, Any]) -> None:
        """
        E5 — Scientific Auditability

        Lei:
        Toda afirmação de conhecimento deve ser:
        - explicável
        - rastreável
        - inspecionável

        Auditoria NÃO significa reproduzir cálculo,
        apenas justificar epistemicamente.
        """

        # E5 é garantido pela existência dos campos exigidos em E1.
        # Este método torna a lei explícita e auditável.
        return
