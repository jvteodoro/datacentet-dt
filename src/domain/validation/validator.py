# domain/validation/validator.py

from dataclasses import dataclass
from typing import Dict, List

from domain.core.snapshot import Snapshot

from domain.contracts.software import SoftwareContract, SoftwareViolation
from domain.contracts.temporal import TemporalContract, TemporalViolation
from domain.contracts.statistical import StatisticalContract, StatisticalViolation
from domain.contracts.epistemic import EpistemicContract, EpistemicViolation
from domain.contracts.model import ModelContract, ModelInvariantViolation
from domain.contracts.hierarchy import HierarchyContract, HierarchyInvariantViolation


# ---------------------------------------------------------------------
# Resultado de validação
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ValidationResult:
    """
    Resultado da validação científica de um Snapshot.
    """
    is_valid: bool
    violations: Dict[str, List[str]]


# ---------------------------------------------------------------------
# Validator — Core
# ---------------------------------------------------------------------

class Validator:
    """
    Validator — Domain Validation Core (FINAL)

    Orquestra a aplicação dos contratos científicos
    sobre as views derivadas de um Snapshot.

    Este componente:
    - é puro
    - é determinístico
    - não mantém estado
    - não executa lógica de domínio
    """

    def validate(self, *, snapshot: Snapshot) -> ValidationResult:
        if not isinstance(snapshot, Snapshot):
            raise TypeError("Validator requires a Snapshot")

        violations: Dict[str, List[str]] = {}

        def record(contract: str, exc: Exception):
            violations.setdefault(contract, []).append(str(exc))

        # -------------------------------------------------
        # Software Contract
        # -------------------------------------------------
        try:
            SoftwareContract().validate(
                snapshot.to_software_view()
            )
        except SoftwareViolation as e:
            record("Software", e)

        # -------------------------------------------------
        # Temporal Contract
        # -------------------------------------------------
        try:
            TemporalContract().validate(
                snapshot.to_temporal_view()
            )
        except TemporalViolation as e:
            record("Temporal", e)

        # -------------------------------------------------
        # Statistical Contract
        # -------------------------------------------------
        try:
            StatisticalContract().validate(
                snapshot.to_statistical_view()
            )
        except StatisticalViolation as e:
            record("Statistical", e)

        # -------------------------------------------------
        # Epistemic Contract
        # (aplicado por afirmação de conhecimento)
        # -------------------------------------------------
        for idx, record_ep in enumerate(snapshot.to_epistemic_view()):
            try:
                EpistemicContract().validate(record_ep)
            except EpistemicViolation as e:
                record(f"Epistemic[{idx}]", e)

        # -------------------------------------------------
        # Model Contract
        # -------------------------------------------------
        try:
            ModelContract().validate(
                snapshot.to_model_view()
            )
        except ModelInvariantViolation as e:
            record("Model", e)

        # -------------------------------------------------
        # Hierarchy Contract
        # -------------------------------------------------
        try:
            HierarchyContract().validate(
                snapshot.to_hierarchy_view()
            )
        except HierarchyInvariantViolation as e:
            record("Hierarchy", e)

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
        )