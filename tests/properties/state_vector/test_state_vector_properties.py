import pytest
import numpy as np
from hypothesis import given, strategies as st

from domain.core.state_variable import StateVariable
from domain.core.state_vector import (
    StateVector,
    StateVectorInvariantViolation,
)

# -------------------------------------------------
# Estratégias
# -------------------------------------------------

valid_names = st.from_regex(r"[A-Za-z_][A-Za-z0-9_]*", fullmatch=True)
valid_values = st.floats(allow_nan=False, allow_infinity=False)
valid_uncertainty = st.floats(min_value=0, allow_nan=False, allow_infinity=False)
valid_timestamp = st.integers()

@st.composite
def state_variables(draw, size=st.integers(min_value=1, max_value=5)):
    n = draw(size)
    timestamp = draw(valid_timestamp)
    names = draw(st.lists(valid_names, min_size=n, max_size=n, unique=True))

    variables = []
    for name in names:
        variables.append(
            StateVariable(
                name=name,
                value=draw(valid_values),
                uncertainty=draw(valid_uncertainty),
                timestamp=timestamp,
            )
        )
    return variables

@st.composite
def valid_covariance(draw, dim):
    mat = draw(
        st.lists(
            st.lists(st.floats(min_value=0, max_value=1), min_size=dim, max_size=dim),
            min_size=dim,
            max_size=dim,
        )
    )
    cov = np.array(mat)
    return cov @ cov.T  # garante semidefinida positiva


# -------------------------------------------------
# Invariantes estruturais
# -------------------------------------------------

@given(variables=state_variables())
def test_SVEC1_to_SVEC3_valid_state_vector_is_created(variables):
    dim = len(variables)
    cov = np.eye(dim)

    sv = StateVector(
        variables=variables,
        covariance=cov,
    )

    assert len(sv.variables) == dim
    assert sv.timestamp == variables[0].timestamp


def test_SVEC2_variable_names_must_be_unique():
    v1 = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    v2 = StateVariable(name="x", value=2.0, uncertainty=0.2, timestamp=0)

    with pytest.raises(StateVectorInvariantViolation):
        StateVector(
            variables=[v1, v2],
            covariance=np.eye(2),
        )


def test_SVEC3_all_variables_must_share_timestamp():
    v1 = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    v2 = StateVariable(name="y", value=2.0, uncertainty=0.2, timestamp=1)

    with pytest.raises(StateVectorInvariantViolation):
        StateVector(
            variables=[v1, v2],
            covariance=np.eye(2),
        )


@given(variables=state_variables())
def test_SVEC4_covariance_dimension_must_match(variables):
    dim = len(variables)

    with pytest.raises(StateVectorInvariantViolation):
        StateVector(
            variables=variables,
            covariance=np.eye(dim + 1),
        )


def test_SVEC6_state_vector_is_immutable():
    v = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    sv = StateVector(variables=[v], covariance=np.eye(1))

    with pytest.raises(StateVectorInvariantViolation):
        sv._variables = []


def test_SVEC5_epistemic_type_is_state_vector():
    v = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    sv = StateVector(variables=[v], covariance=np.eye(1))

    data = sv.to_dict()
    assert data["epistemic_type"] == "state_vector"


def test_SVEC4_covariance_is_symmetrized_on_creation():
    v1 = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    v2 = StateVariable(name="y", value=2.0, uncertainty=0.1, timestamp=0)

    cov = np.array(
        [
            [1.0, 0.2],
            [0.2000000001, 1.0],
        ]
    )

    sv = StateVector(variables=[v1, v2], covariance=cov)

    assert np.allclose(sv.covariance, sv.covariance.T)


def test_SVEC4_invalid_covariance_raises_clear_domain_message():
    v = StateVariable(name="x", value=1.0, uncertainty=0.1, timestamp=0)
    cov = np.array([[-1.0]])

    with pytest.raises(StateVectorInvariantViolation, match="invalid covariance matrix"):
        StateVector(variables=[v], covariance=cov)
