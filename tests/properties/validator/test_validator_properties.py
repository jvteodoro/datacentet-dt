import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot, SnapshotInvariantViolation
from domain.validation.validator import (
    Validator,
    ValidationResult,
)


def test_validator_accepts_valid_snapshot():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=0,
            source="sensor",
        )
    ]

    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=5.0,
                uncertainty=0.2,
                timestamp=0,
            )
        ],
        covariance=np.array([[0.2]]),
    )

    snap = Snapshot(
        observables=obs,
        state_vector=sv,
        parameters=[],
    )

    validator = Validator()
    result = validator.validate(snapshot=snap)

    assert isinstance(result, ValidationResult)
    assert result.is_valid is True
    assert result.violations == {}


def test_validator_reports_violations():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=1,
            source="sensor",
        )
    ]

    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=5.0,
                uncertainty=0.2,
                timestamp=0,  # desalinhado
            )
        ],
        covariance=np.array([[0.2]]),
    )

    with pytest.raises(SnapshotInvariantViolation, match="SN9"):
        Snapshot(
            observables=obs,
            state_vector=sv,
            parameters=[],
        )