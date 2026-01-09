import pytest
from typing import Dict
import numpy as np

from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable
from domain.core.observation_model import (
    ObservationModel,
    PredictedObservable,
    ObservationModelInvariantViolation,
)


# -------------------------------------------------
# Fakes mínimos para teste
# -------------------------------------------------

class LinearObservationModel(ObservationModel):
    """
    Modelo fake: y = x * gain
    """

    def predicted_observables(self):
        return ["y"]

    def _predict(self, state_vector, parameters):
        x = state_vector.variables[0].value
        gain = parameters[0].estimated_value if parameters else 1.0
        return {
            "y": x * gain
        }


# -------------------------------------------------
# Testes
# -------------------------------------------------

def test_OM1_prediction_is_deterministic():
    sv = StateVector(
        variables=[
            StateVariable(name="x", value=2.0, uncertainty=0.1, timestamp=0)
        ],
        covariance=np.array([[0.1]]),
    )

    param = Identifiable(
        name="gain",
        estimated_value=3.0,
        uncertainty=0.2,
        timestamp=0,
        method="assumed",
        support=["x"],
    )

    model = LinearObservationModel()

    p1 = model.predict(state_vector=sv, parameters=[param])
    p2 = model.predict(state_vector=sv, parameters=[param])

    assert p1["y"].predicted_value == p2["y"].predicted_value


def test_OM2_only_declared_observables_are_predicted():
    sv = StateVector(
        variables=[
            StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
        ],
        covariance=np.array([[0.1]]),
    )

    model = LinearObservationModel()
    preds = model.predict(state_vector=sv, parameters=[])

    assert set(preds.keys()) == {"y"}


def test_OM5_predicted_observables_inherit_timestamp():
    sv = StateVector(
        variables=[
            StateVariable(name="x", value=5.0, uncertainty=0.1, timestamp=42)
        ],
        covariance=np.array([[0.1]]),
    )

    model = LinearObservationModel()
    preds = model.predict(state_vector=sv, parameters=[])

    assert preds["y"].timestamp == 42


def test_residual_computation():
    predicted = PredictedObservable(
        name="y",
        predicted_value=10.0,
        timestamp=0,
    )

    residual = ObservationModel.residual(
        predicted=predicted,
        observed_value=8.0,
    )

    # Residual is defined as observed - predicted (innovation form)
    assert residual == -2.0
