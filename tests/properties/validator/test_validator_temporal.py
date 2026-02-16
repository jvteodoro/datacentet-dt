import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_T3_observable_from_future_is_rejected():
    obs = Observable(
        name="y",
        value=5.0,
        uncertainty=0.1,
        timestamp=5,
        source="sensor",
    )

    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=2.0,
                uncertainty=0.2,
                timestamp=3,
            )
        ],
        covariance=np.array([[0.2]]),
    )

    snap = Snapshot(
        observables=[obs],
        state_vector=sv,
        parameters=[],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Temporal" in result.violations