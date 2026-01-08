"""
Validator — Domain Validation Core (BASELINE v1.0)

Aplica contratos científicos a um Snapshot.
"""

from dataclasses import dataclass
from typing import Dict, List

from domain.core.snapshot import Snapshot

# Importa contratos
from domain.contracts.software import SoftwareViolation
from domain.contracts.temporal import TemporalViolation
from domain.contracts.statistical import StatisticalViolation
from domain.contracts.epistemic import EpistemicViolation
from domain.contracts.model import ModelInvariantViolation
from domain.contracts.hierarchy import HierarchyInvariantViolation


@dataclass(frozen=True)
class ValidationResult:
    """
    Resultado da validação científica de um Snapshot.
    """
    is_valid: bool
    violations: Dict[str, List[str]]


class Validator:
    """
    Validator (Design by Contract).

    Avalia admissibilidade científica de um Snapshot.
    """

    def validate(self, *, snapshot: Snapshot) -> ValidationResult:
        if not isinstance(snapshot, Snapshot):
            raise TypeError("Validator requires a Snapshot")

        violations: Dict[str, List[str]] = {}

        def record(contract: str, exc: Exception):
            violations.setdefault(contract, []).append(str(exc))

        # -------------------------------------------------
        # Aplicação dos contratos
        # -------------------------------------------------

        try:
            self._validate_software(snapshot)
        except SoftwareViolation as e:
            record("Software", e)

        try:
            self._validate_temporal(snapshot)
        except TemporalViolation as e:
            record("Temporal", e)

        try:
            self._validate_statistical(snapshot)
        except StatisticalViolation as e:
            record("Statistical", e)

        try:
            self._validate_epistemic(snapshot)
        except EpistemicViolation as e:
            record("Epistemic", e)

        try:
            self._validate_model(snapshot)
        except ModelInvariantViolation as e:
            record("Model", e)

        try:
            self._validate_hierarchy(snapshot)
        except HierarchyInvariantViolation as e:
            record("Hierarchy", e)

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
        )

    # -------------------------------------------------
    # Validadores específicos (stubs iniciais)
    # -------------------------------------------------

    def _validate_software(self, snapshot: Snapshot):
        # Estrutura já garantida pelos objetos
        pass

    def _validate_temporal(self, snapshot: Snapshot):
        # Exemplo: timestamps já coerentes pelo Snapshot
        pass

    def _validate_statistical(self, snapshot: Snapshot):
        # Exemplo: covariância válida já garantida
        pass

    def _validate_epistemic(self, snapshot: Snapshot):
        # Exemplo: Identifiables e Observables já auditáveis
        pass

    def _validate_model(self, snapshot: Snapshot):
        # Será expandido com resíduos, compatibilidade etc.
        pass

    def _validate_hierarchy(self, snapshot: Snapshot):
        # Aplicável quando houver hierarquia
        pass