import pytest
from hypothesis import given, strategies as st

from domain.core.identifiable import (
    Identifiable,
    IdentifiableInvariantViolation,
)


# -------------------------
# Estratégias
# -------------------------

valid_names = st.from_regex(r"[A-Za-z_][A-Za-z0-9_]*", fullmatch=True)
valid_methods = st.from_regex(r"[A-Za-z_][A-Za-z0-9_]*", fullmatch=True)
valid_support = st.lists(st.text(min_size=1), min_size=1)
valid_values = st.floats(allow_nan=False, allow_infinity=False)
valid_uncertainty = st.floats(min_value=0, allow_nan=False, allow_infinity=False)
valid_confidence = st.floats(min_value=1e-6, max_value=1.0)
valid_timestamps = st.integers()


# -------------------------
# Invariantes estruturais
# -------------------------

@given(
    name=valid_names,
    value=valid_values,
    uncertainty=valid_uncertainty,
    timestamp=valid_timestamps,
    method=valid_methods,
    support=valid_support,
)
def test_I1_to_I6_identifiable_with_uncertainty_is_created(
    name, value, uncertainty, timestamp, method, support
):
    ident = Identifiable(
        name=name,
        estimated_value=value,
        uncertainty=uncertainty,
        timestamp=timestamp,
        method=method,
        support=support,
    )

    assert ident.name == name
    assert ident.estimated_value == value
    assert ident.uncertainty == uncertainty
    assert ident.timestamp == timestamp
    assert ident.method == method
    assert ident.support == support


@given(
    name=valid_names,
    value=valid_values,
    confidence=valid_confidence,
    timestamp=valid_timestamps,
    method=valid_methods,
    support=valid_support,
)
def test_I3_identifiable_with_confidence_is_created(
    name, value, confidence, timestamp, method, support
):
    ident = Identifiable(
        name=name,
        estimated_value=value,
        confidence=confidence,
        timestamp=timestamp,
        method=method,
        support=support,
    )

    assert ident.confidence == confidence
    assert ident.uncertainty is None


def test_I3_requires_uncertainty_or_confidence():
    with pytest.raises(IdentifiableInvariantViolation):
        Identifiable(
            name="efficiency",
            estimated_value=0.9,
            timestamp=0,
            method="least_squares",
            support=["voltage", "current"],
        )


def test_I7_identifiable_is_immutable():
    ident = Identifiable(
        name="resistance",
        estimated_value=10.0,
        uncertainty=0.5,
        timestamp=1,
        method="regression",
        support=["voltage", "current"],
    )

    with pytest.raises(IdentifiableInvariantViolation):
        ident._estimated_value = 12.0


def test_I6_epistemic_type_is_inferred():
    ident = Identifiable(
        name="loss_factor",
        estimated_value=0.1,
        uncertainty=0.02,
        timestamp=5,
        method="model_fit",
        support=["power_in", "power_out"],
    )

    data = ident.to_dict()
    assert data["epistemic_type"] == "inferred"
