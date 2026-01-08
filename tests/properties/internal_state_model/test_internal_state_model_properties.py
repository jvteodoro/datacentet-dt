import pytest
import numpy as np

from domain.core.observable import Observable
from domain.core.observable_registry import ObservableRegistry
from domain.core.identifiable_registry import IdentifiableRegistry
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot
from domain.core.internal_state_model import InternalStateModel


class DummyEstimator:
    def estimate(self, observables):
        return StateVector(
            variables=[
                StateVariable(
                    name="x",
                    value=1.0,
                    uncertainty=0.5,
                    timestamp=observables[-1].timestamp,
                )
            ],
            covariance=np.array([[0.5]]),
        )


class DummyIdentifier:
    def identify(self, state_vector):
        return []


def test_ISM_produces_snapshot_from_observations():
    obs_reg = ObservableRegistry()
    id_reg = IdentifiableRegistry()

    ism = InternalStateModel(
        observable_registry=obs_reg,
        identifiable_registry=id_reg,
        state_estimator=DummyEstimator(),
        parameter_identifier=DummyIdentifier(),
    )

    obs = Observable(
        name="y",
        value=10.0,
        uncertainty=0.2,
        timestamp=1,
        source="sensor",
    )

    ism.ingest_observation(obs)

    snap = ism.step(timestamp=1)

    assert isinstance(snap, Snapshot)
    assert snap.state_vector is not None
    assert snap.observables == [obs]


def test_ISM_returns_none_if_no_observations():
    obs_reg = ObservableRegistry()
    id_reg = IdentifiableRegistry()

    ism = InternalStateModel(
        observable_registry=obs_reg,
        identifiable_registry=id_reg,
        state_estimator=DummyEstimator(),
        parameter_identifier=DummyIdentifier(),
    )

    snap = ism.step(timestamp=0)

    assert snap is None