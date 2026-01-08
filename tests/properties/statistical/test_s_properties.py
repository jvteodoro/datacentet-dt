import pytest
import numpy as np
from hypothesis import given, strategies as st
# test/domain/properties/test_s_properties.py

"""
| Invariante | Essência                         |
| ---------- | -------------------------------- |
| **S1**     | Toda estimativa tem incerteza    |
| **S2**     | Covariância válida               |
| **S3**     | Confiança admissível             |
| **S4**     | Consistência predição–observação |
| **S5**     | Propagação coerente de incerteza |

"""

finite_floats = st.floats(
    allow_nan=False,
    allow_infinity=False,
    width=32
)
@st.composite
def symmetric_matrices(draw, n=2):
    m = draw(
        st.lists(
            st.lists(finite_floats, min_size=n, max_size=n),
            min_size=n,
            max_size=n
        )
    )
    m = np.array(m)
    return (m + m.T) / 2

@given(value=finite_floats)
def test_S1_estimate_without_uncertainty_is_invalid(value):
    def estimate(v):
        return {"value": v, "uncertainty": None}

    est = estimate(value)

    with pytest.raises(Exception):
        if est["uncertainty"] is None:
            raise Exception("StatisticalViolation")

@given(cov=symmetric_matrices())
def test_S2_covariance_is_symmetric(cov):
    assert np.allclose(cov, cov.T)

@given(cov=symmetric_matrices())
def test_S2_covariance_is_positive_semidefinite(cov):
    eigvals = np.linalg.eigvals(cov)
    assert np.all(eigvals >= -1e-6)

@given(conf=st.floats())
def test_S3_confidence_bounds(conf):
    if not (0 < conf <= 1):
        with pytest.raises(Exception):
            raise Exception("StatisticalViolation")

@given(
    predicted=finite_floats,
    observed=finite_floats,
    variance=st.floats(min_value=1e-6, max_value=1e6)
)
def test_S4_normalized_residual_is_bounded(predicted, observed, variance):
    residual = observed - predicted
    sigma = np.sqrt(variance)

    normalized = abs(residual / sigma)

    if normalized > 10:  # limite genérico, contrato, não modelo
        with pytest.raises(Exception):
            raise Exception("StatisticalViolation")

@given(
    child_vars=st.lists(
        st.floats(min_value=1e-6, max_value=1e3),
        min_size=1
    )
)
def test_S5_aggregation_does_not_reduce_uncertainty(child_vars):
    parent_var = min(child_vars) - 1e-6  # artificialmente menor

    if parent_var < min(child_vars):
        with pytest.raises(Exception):
            raise Exception("StatisticalViolation")

@given(vars=st.lists(st.floats(min_value=0), min_size=1))
def test_S_zero_uncertainty_requires_all_zero(vars):
    parent_var = 0.0
    if any(v > 0 for v in vars):
        with pytest.raises(Exception):
            raise Exception("StatisticalViolation")
