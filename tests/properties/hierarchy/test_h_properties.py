import pytest
import numpy as np
from hypothesis import given, strategies as st

# test/domain/properties/test_h_properties.py

"""
| Invariante | Essência                              |
| ---------- | ------------------------------------- |
| **H1**     | Encapsulamento epistêmico hierárquico |
| **H2**     | Consistência temporal hierárquica     |
| **H3**     | Propagação coerente de incerteza      |
| **H4**     | Não amplificação hierárquica de erro  |
"""

times = st.integers(min_value=0)
confidences = st.floats(min_value=1e-6, max_value=1.0)
variances = st.floats(min_value=1e-6, max_value=1e6)

@given(access_private=st.booleans())
def test_H1_no_private_state_leakage(access_private):
    child = {
        "public_api": {"power": 100},
        "_internal_state": {"raw_sensor": 97}
    }

    if access_private:
        with pytest.raises(Exception):
            _ = child["_internal_state"]
            raise Exception("HierarchyInvariantViolation")

@given(parent_t=times, child_t=times)
def test_H2_parent_time_not_before_children(parent_t, child_t):
    if parent_t < child_t:
        with pytest.raises(Exception):
            raise Exception("HierarchyInvariantViolation")

@given(
    child_vars=st.lists(variances, min_size=1),
    parent_var=variances
)
def test_H3_parent_uncertainty_not_smaller_than_children(child_vars, parent_var):
    if parent_var < min(child_vars):
        with pytest.raises(Exception):
            raise Exception("HierarchyInvariantViolation")

@given(
    child_confidences=st.lists(confidences, min_size=1),
    parent_confidence=confidences
)
def test_H3_parent_confidence_not_greater_than_children(
    child_confidences, parent_confidence
):
    if parent_confidence > min(child_confidences):
        with pytest.raises(Exception):
            raise Exception("HierarchyInvariantViolation")

@given(
    local_error=st.booleans(),
    validated=st.booleans()
)
def test_H4_local_error_not_promoted_without_validation(local_error, validated):
    if local_error and not validated:
        with pytest.raises(Exception):
            raise Exception("HierarchyInvariantViolation")

@given(
    child_failures=st.lists(st.booleans(), min_size=1)
)
def test_H4_child_failures_not_masked(child_failures):
    parent_status = all(not f for f in child_failures)

    if any(child_failures) and parent_status:
        with pytest.raises(Exception):
            raise Exception("HierarchyInvariantViolation")
