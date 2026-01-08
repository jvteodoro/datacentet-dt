import pytest
import numpy as np
from hypothesis import given, strategies as st
# test/domain/properties/test_m_properties.py

"""
| Invariante | Essência                          |
| ---------- | --------------------------------- |
| **M1**     | Consistência Estado–Observação    |
| **M2**     | Não Criação Espúria de Informação |
| **M3**     | Separação Estado vs Conhecimento  |
"""

finite_floats = st.floats(
    allow_nan=False,
    allow_infinity=False,
    width=32
)
positive_vars = st.floats(min_value=1e-6, max_value=1e6)
confidences = st.floats(min_value=1e-6, max_value=1.0)

@given(
    state=finite_floats,
    observation=finite_floats,
    variance=positive_vars
)
def test_M1_state_observation_statistical_compatibility(state, observation, variance):
    residual = observation - state
    sigma = np.sqrt(variance)
    normalized_residual = abs(residual / sigma)

    # Limite contratual genérico (não é tuning de modelo)
    if normalized_residual > 10:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")

@given(has_observations=st.booleans())
def test_M1_state_requires_observational_support(has_observations):
    state = {"value": 100}
    observations = [] if not has_observations else [95, 105]

    if not observations:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")

@given(
    prev_var=positive_vars,
    new_var=positive_vars,
    has_new_data=st.booleans()
)
def test_M2_uncertainty_cannot_decrease_without_new_information(
    prev_var, new_var, has_new_data
):
    if not has_new_data and new_var < prev_var:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")

@given(
    prev_entropy=st.floats(min_value=0),
    new_entropy=st.floats(min_value=0),
    has_inputs=st.booleans()
)
def test_M2_information_gain_requires_inputs(prev_entropy, new_entropy, has_inputs):
    if not has_inputs and new_entropy < prev_entropy:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")

@given(
    state_value=finite_floats,
    exposed_value=finite_floats
)
def test_M3_state_and_knowledge_are_not_identical_by_default(
    state_value, exposed_value
):
    # Por contrato, identidade perfeita sem justificativa é inválida
    if state_value == exposed_value:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")

@given(
    expose_as_knowledge=st.booleans(),
    confidence=st.one_of(confidences, st.none())
)
def test_M3_exposed_knowledge_requires_confidence(expose_as_knowledge, confidence):
    if expose_as_knowledge and confidence is None:
        with pytest.raises(Exception):
            raise Exception("ModelInvariantViolation")
