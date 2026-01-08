import pytest
from hypothesis import given, strategies as st

from src.domain.core.observable import Observable, ObservableInvariantViolation


# -------------------------
# Estratégias
# -------------------------

valid_names = st.text(min_size=1)
valid_sources = st.text(min_size=1)
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
    source=valid_sources,
)
def test_O1_to_O5_valid_observable_is_created(
    name, value, uncertainty, timestamp, source
):
    obs = Observable(
        name=name,
        value=value,
        uncertainty=uncertainty,
        timestamp=timestamp,
        source=source,
    )

    assert obs.name == name
    assert obs.value == value
    assert obs.uncertainty == uncertainty
    assert obs.timestamp == timestamp
    assert obs.source == source


def test_O3_uncertainty_must_be_non_negative():
    with pytest.raises(ObservableInvariantViolation):
        Observable(
            name="voltage",
            value=220.0,
            uncertainty=-1.0,
            timestamp=0,
            source="sensor",
        )


def test_O6_observable_is_immutable():
    obs = Observable(
        name="temperature",
        value=25.0,
        uncertainty=0.5,
        timestamp=10,
        source="sensor",
    )

    with pytest.raises(ObservableInvariantViolation):
        obs._value = 30.0


def test_O7_observable_is_epistemically_neutral():
    obs = Observable(
        name="current",
        value=10.0,
        uncertainty=0.2,
        timestamp=5,
        source="sensor",
    )

    data = obs.to_dict()
    assert data["epistemic_type"] == "observed"
