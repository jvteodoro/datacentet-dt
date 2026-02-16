import pytest
import numpy as np

from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_M1_state_without_observations_is_invalid():
    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=10.0,
                uncertainty=0.5,
                timestamp=0,
            )
        ],
        covariance=np.array([[0.5]]),
    )

    snap = Snapshot(
        observables=[],
        state_vector=sv,
        parameters=[],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Model" in result.violations