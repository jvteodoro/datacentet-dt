import pytest

from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable
from domain.core.parameter_identifier import (
    ParameterIdentifier,
    ParameterIdentifierInvariantViolation,
)


# -------------------------------------------------
# Fake Identifier
# -------------------------------------------------

class ConstantGainIdentifier(ParameterIdentifier):
    """
    Identificador fake: retorna ganho constante
    """

    def _identify(self, *, observables, state_vector):
        ts = None
        if observables:
            ts = observables[0].timestamp
        elif state_vector:
            ts = state_vector.timestamp

        return [
            Identifiable(
                name="gain",
                estimated_value=2.0,
                uncertainty=0.1,
                timestamp=ts,
                method="constant_assumption",
                support=["y"],
            )
        ]


# -------------------------------------------------
# Testes
# -------------------------------------------------

def test_PI2_identifier_returns_identifiables():
    obs = [
        Observable(
            name="y",
            value=10.0,
            uncertainty=0.5,
            timestamp=0,
            source="sensor",
        )
    ]

    identifier = ConstantGainIdentifier()

    params = identifier.identify(
        observables=obs,
        state_vector=None,
    )

    assert isinstance(params, list)
    assert all(isinstance(p, Identifiable) for p in params)


def test_PI3_parameter_timestamp_not_from_future():
    sv = StateVector(
        variables=[
            StateVariable(
                name="x",
                value=5.0,
                uncertainty=0.2,
                timestamp=3,
            )
        ],
        covariance=[[0.2]],
    )

    identifier = ConstantGainIdentifier()

    params = identifier.identify(
        observables=[],
        state_vector=sv,
    )

    assert params[0].timestamp <= sv.timestamp


def test_PI1_identifier_does_not_return_state():
    identifier = ConstantGainIdentifier()

    with pytest.raises(ParameterIdentifierInvariantViolation):
        identifier._validate_output([StateVariable(
            name="x", value=1.0, uncertainty=0.1, timestamp=0
        )])