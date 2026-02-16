import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_S5_observation_cannot_be_more_certain_than_state():
    obs = Observable(
        name="y",
        value=10.0,
        uncertainty=0.01,  # muito menor
        timestamp=0,
        source="sensor",
    )

    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=9.8,
                uncertainty=1.0,
                timestamp=0,
            )
        ],
        covariance=np.array([[1.0]]),
    )

    snap = Snapshot(
        observables=[obs],
        state_vector=sv,
        parameters=[],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Statistical" in result.violations