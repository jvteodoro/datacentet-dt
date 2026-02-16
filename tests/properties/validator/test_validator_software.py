import pytest
import numpy as np

from domain.core.snapshot import Snapshot
from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable
from domain.validation.validator import Validator


def valid_snapshot():
    obs = [
        Observable(
            name="voltage",
            value=230.0,
            uncertainty=1.0,
            timestamp=0,
            source="sensor",
        )
    ]

    sv = StateVector(
        variables=[
            StateVariable(
                name="v",
                value=230.0,
                uncertainty=1.0,
                timestamp=0,
            )
        ],
        covariance=np.array([[1.0]]),
    )

    param = Identifiable(
        name="resistance",
        estimated_value=0.5,
        uncertainty=0.1,
        timestamp=0,
        method="least_squares",
        support=["voltage"],
    )

    return Snapshot(
        observables=obs,
        state_vector=sv,
        identifiables=[param],
        component_id="comp-1",
        component_type="energy",
        name="EnergySubsystem",
        version="1.0.0",
        declared_invariants=["SW1", "SW2"],
        dependencies=[],
    )


def test_SW_invalid_version_is_rejected():
    snap = valid_snapshot()

    bad = Snapshot(
        observables=snap.observables,
        state_vector=snap.state_vector,
        identifiables=snap.identifiables,
        component_id="comp-1",
        component_type="energy",
        name="EnergySubsystem",
        version="1",  # inválido
        declared_invariants=["SW1"],
        dependencies=[],
    )

    result = Validator().validate(snapshot=bad)
    assert not result.is_valid
    assert "Software" in result.violations