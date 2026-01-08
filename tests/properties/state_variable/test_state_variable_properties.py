import pytest
from hypothesis import given, strategies as st

from domain.core.state_variable import (
    StateVariable,
    StateVariableInvariantViolation,
)

# -------------------------
# Estratégias
# -------------------------

valid_names = st.from_regex(r"[A-Za-z_][A-Za-z0-9_]*", fullmatch=True)
valid_values = st.floats(allow_nan=False, allow_infinity=False)
valid_uncertainty = st.floats(min_value=0, allow_nan=False, allow_infinity=False)
valid_timestamps = st.integers()

# -------------------------
# Invariantes estruturais
# -------------------------

@given(
    name=valid_names,
    value=valid_values,
    uncertainty=valid_uncertainty,
    timestamp=valid_timestamps,
)
def test_SV1_to_SV6_valid_state_variable_is_created(
    name, value, uncertainty, timestamp
):
    sv = StateVariable(
        name=name,
        value=value,
        uncertainty=uncertainty,
        timestamp=timestamp,
    )

    assert sv.name == name
    assert sv.value == value
    assert sv.uncertainty == uncertainty
    assert sv.timestamp == timestamp


def test_SV3_uncertainty_must_be_non_negative():
    with pytest.raises(StateVariableInvariantViolation):
        StateVariable(
            name="energy",
            value=100.0,
            uncertainty=-0.1,
            timestamp=0,
        )


def test_SV7_state_variable_is_immutable():
    sv = StateVariable(
        name="temperature_internal",
        value=40.0,
        uncertainty=0.5,
        timestamp=10,
    )

    with pytest.raises(StateVariableInvariantViolation):
        sv._value = 42.0


def test_SV5_epistemic_type_is_state():
    sv = StateVariable(
        name="charge",
        value=0.8,
        uncertainty=0.1,
        timestamp=3,
    )

    data = sv.to_dict()
    assert data["epistemic_type"] == "state"
