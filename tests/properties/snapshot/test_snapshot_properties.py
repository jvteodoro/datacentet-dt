import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable
from domain.core.snapshot import (
    Snapshot,
    SnapshotInvariantViolation,
)


def test_SN1_snapshot_is_immutable():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=0,
            source="sensor",
        )
    ]

    snap = Snapshot(
        observables=obs,
        state_vector=None,
        parameters=[],
    )

    with pytest.raises(SnapshotInvariantViolation):
        snap._observables = []


def test_SN2_all_components_share_timestamp():
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
                timestamp=0,
            )
        ],
        covariance=np.array([[0.2]]),
    )

    with pytest.raises(SnapshotInvariantViolation):
        Snapshot(
            observables=obs,
            state_vector=sv,
            parameters=[],
        )


def test_SN4_snapshot_requires_state_or_observables():
    with pytest.raises(SnapshotInvariantViolation):
        Snapshot(
            observables=[],
            state_vector=None,
            parameters=[],
        )


def test_SN3_separation_of_epistemic_roles():
    obs = Observable(
        name="y",
        value=10.0,
        uncertainty=0.5,
        timestamp=0,
        source="sensor",
    )

    with pytest.raises(SnapshotInvariantViolation):
        Snapshot(
            observables=[obs],
            state_vector=obs,  # tipo errado
            parameters=[],
        )


def test_to_dict_contains_all_components():
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

    param = Identifiable(
        name="gain",
        estimated_value=2.0,
        uncertainty=0.1,
        timestamp=0,
        method="assumed",
        support=["y"],
    )

    snap = Snapshot(
        observables=obs,
        state_vector=sv,
        parameters=[param],
    )

    data = snap.to_dict()

    assert "observables" in data
    assert "state_vector" in data
    assert "parameters" in data
    assert data["timestamp"] == 0