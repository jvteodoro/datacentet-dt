import pytest
import numpy as np

from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.observable import Observable
from domain.core.observation_model import ObservationModel
from domain.core.state_estimator import (
    StateEstimator,
    StateEstimatorInvariantViolation,
)


# -------------------------------------------------
# Fake Observation Model
# -------------------------------------------------

class IdentityObservationModel(ObservationModel):
    """
    Modelo fake: y = x
    """

    def predicted_observables(self):
        return ["y"]

    def _predict(self, state_vector, parameters):
        return {"y": state_vector.variables[0].value}


# -------------------------------------------------
# Fake Estimator
# -------------------------------------------------

class SimpleStateEstimator(StateEstimator):
    """
    Estimador fake: x_k = média das observações
    """

    def _estimate(self, *, observables, previous_state, model):
        values = [obs.value for obs in observables]
        mean = sum(values) / len(values)

        return StateVector(
            variables=[
                StateVariable(
                    name="x",
                    value=mean,
                    uncertainty=0.1,
                    timestamp=observables[0].timestamp,
                )
            ],
            covariance=np.array([[0.1]]),
        )


# -------------------------------------------------
# Testes
# -------------------------------------------------

def test_SE2_estimator_returns_state_vector():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=0,
            source="sensor",
        )
    ]

    estimator = SimpleStateEstimator()
    model = IdentityObservationModel()

    state = estimator.estimate(
        observables=obs,
        observation_model=model,
        previous_state=None,
    )

    assert isinstance(state, StateVector)


def test_SE3_timestamp_is_monotonic():
    prev = StateVector(
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

    obs = [
        Observable(
            name="y",
            value=6.0,
            uncertainty=0.3,
            timestamp=1,
            source="sensor",
        )
    ]

    estimator = SimpleStateEstimator()
    model = IdentityObservationModel()

    new_state = estimator.estimate(
        observables=obs,
        observation_model=model,
        previous_state=prev,
    )

    assert new_state.timestamp >= prev.timestamp
