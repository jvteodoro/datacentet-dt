"""
Statistical Domain Contract — BASELINE v1.0 (REFINED)

Este módulo define as LEIS ESTATÍSTICAS do Domain Level.

Ele NÃO:
- assume distribuições
- implementa filtros
- realiza inferência
- aprende parâmetros
- corrige medições

Pergunta respondida:
→ "Dado um snapshot, a incerteza declarada é matematicamente
   e cientificamente admissível?"
"""

from typing import Any, Dict, List
import numpy as np

from domain.core.covariance_utils import (
    CovarianceDomainViolation,
    validate_psd_covariance,
)


class StatisticalViolation(Exception):
    """
    Violação de contrato estatístico do Domain Level.

    Indica inconsistência matemática, probabilística
    ou epistemológica na representação da incerteza.
    """
    pass


class StatisticalContract:
    """
    Contrato estatístico do Domain Level.

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
    # Campos semanticamente esperados (não obrigatórios simultaneamente):
    # - uncertainty
    # - covariance: np.ndarray
    # - confidence: float
    # - predicted_value: float
    # - observed_value: float
    # - variance: float
    # - child_variances: List[float]
    #
    # O contrato valida LEIS, não formatos rígidos.
    # ------------------------------------------------------------------

    def validate(self, snapshot: Dict[str, Any]) -> None:
        """
        Valida o snapshot contra os invariantes estatísticos S1–S5.

        Método:
        - puro
        - determinístico
        - sem efeitos colaterais

        Falha explicitamente com StatisticalViolation.
        """

        self._validate_S1_uncertainty(snapshot)
        self._validate_S2_covariance(snapshot)
        self._validate_S3_confidence(snapshot)
        self._validate_S4_consistency(snapshot)
        self._validate_S5_propagation(snapshot)

    # ------------------------------------------------------------------
    # S1 — Toda estimativa tem incerteza
    # ------------------------------------------------------------------

    def _validate_S1_uncertainty(self, snapshot: Dict[str, Any]) -> None:
        """
        S1 — Explicit Uncertainty

        Lei:
        Nenhuma estimativa estatística é válida
        sem uma representação explícita de incerteza.

        Falhas cobertas:
        - supressão artificial de incerteza
        """

        if "estimate" in snapshot and "uncertainty" not in snapshot:
            raise StatisticalViolation(
                "S1: estimate declared without explicit uncertainty"
            )

        if snapshot.get("uncertainty") is None and "estimate" in snapshot:
            raise StatisticalViolation(
                "S1: uncertainty must not be None when estimate exists"
            )

    # ------------------------------------------------------------------
    # S2 — Covariância válida
    # ------------------------------------------------------------------

    def _validate_S2_covariance(self, snapshot: Dict[str, Any]) -> None:
        """
        S2 — Valid Covariance

        Lei:
        Toda matriz de covariância deve ser:
        - quadrada
        - simétrica
        - semidefinida positiva

        A tolerância numérica para PSD é padronizada em
        PSD_EIGENVALUE_TOLERANCE = -1e-9.

        Esta é uma LEI matemática, não heurística.
        """

        cov = snapshot.get("covariance")
        if cov is None:
            return

        try:
            validate_psd_covariance(cov, context="S2 covariance")
        except CovarianceDomainViolation as exc:
            raise StatisticalViolation(str(exc)) from exc

    # ------------------------------------------------------------------
    # S3 — Confiança admissível
    # ------------------------------------------------------------------

    def _validate_S3_confidence(self, snapshot: Dict[str, Any]) -> None:
        """
        S3 — Admissible Confidence

        Lei:
        Confiança deve pertencer ao intervalo (0, 1].

        Confiança NÃO é verdade.
        """

        confidence = snapshot.get("confidence")
        if confidence is None:
            return

        if not isinstance(confidence, (int, float)):
            raise StatisticalViolation("S3: confidence must be numeric")

        if not (0 < confidence <= 1):
            raise StatisticalViolation("S3: confidence must be in (0, 1]")

    # ------------------------------------------------------------------
    # S4 — Consistência predição–observação
    # ------------------------------------------------------------------

    def _validate_S4_consistency(self, snapshot: Dict[str, Any]) -> None:
        """
        S4 — Prediction–Observation Consistency

        Lei:
        Predições e observações devem ser estatisticamente compatíveis.

        O critério é CONTRATUAL:
        - evita incompatibilidades extremas
        - não assume distribuição
        """

        required = {"predicted_value", "observed_value", "variance"}
        if not required.issubset(snapshot):
            return

        predicted = snapshot["predicted_value"]
        observed = snapshot["observed_value"]
        variance = snapshot["variance"]

        if variance <= 0:
            raise StatisticalViolation("S4: variance must be positive")

        residual = observed - predicted
        sigma = np.sqrt(variance)
        normalized = abs(residual / sigma)

        limit = snapshot.get("consistency_limit", 10.0)

        if normalized > limit:
            raise StatisticalViolation(
                "S4: prediction and observation are statistically incompatible"
            )

    # ------------------------------------------------------------------
    # S5 — Propagação coerente de incerteza
    # ------------------------------------------------------------------

    def _validate_S5_propagation(self, snapshot: Dict[str, Any]) -> None:
        """
        S5 — Coherent Uncertainty Propagation

        Lei:
        Agregação NÃO pode reduzir incerteza
        sem nova evidência informacional.

        Esta é uma lei epistemológica.
        """

        parent_var = snapshot.get("parent_variance")
        child_vars: List[float] = snapshot.get("child_variances")

        if parent_var is None or child_vars is None:
            return

        if not child_vars:
            raise StatisticalViolation("S5: aggregation requires child variances")

        if parent_var < min(child_vars):
            raise StatisticalViolation(
                "S5: parent uncertainty cannot be smaller than children uncertainties"
            )

        # Caso limite explícito: certeza zero
        if parent_var == 0.0 and any(v > 0 for v in child_vars):
            raise StatisticalViolation(
                "S5: zero uncertainty requires all sources to be zero-uncertainty"
            )
