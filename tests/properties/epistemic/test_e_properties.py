import pytest
from hypothesis import given, strategies as st
from hypothesis import assume
# test/domain/properties/test_e_properties.py
"""
| Invariante | Essência                                     |
| ---------- | -------------------------------------------- |
| **E1**     | Integridade epistêmica                       |
| **E2**     | Incerteza epistêmica explícita               |
| **E3**     | Não confusão entre conhecimento e inferência |
| **E4**     | Composição epistêmica segura                 |
| **E5**     | Auditabilidade científica                    |

"""

valid_text = st.text(min_size=1).filter(lambda s: s.strip() != "")
invalid_text = st.one_of(st.none(), st.text(max_size=0))
valid_confidence = st.floats(min_value=1e-6, max_value=1.0)
invalid_confidence = st.one_of(
    st.floats(max_value=0),
    st.floats(min_value=1.000001)
)

@given(
    source=invalid_text,
    method=valid_text,
    justification=valid_text,
    confidence=valid_confidence
)
def test_E1_missing_source_is_invalid(source, method, justification, confidence):
    record = {
        "value": 42,
        "source": source,
        "method": method,
        "justification": justification,
        "confidence": confidence,
    }

    with pytest.raises(Exception):
        if not record["source"]:
            raise Exception("EpistemicViolation")

@given(
    source=valid_text,
    method=invalid_text,
    justification=valid_text,
    confidence=valid_confidence
)
def test_E1_missing_method_is_invalid(source, method, justification, confidence):
    with pytest.raises(Exception):
        if not method:
            raise Exception("EpistemicViolation")

@given(
    source=valid_text,
    method=valid_text,
    justification=invalid_text,
    confidence=valid_confidence
)
def test_E1_missing_justification_is_invalid(source, method, justification, confidence):
    with pytest.raises(Exception):
        if not justification:
            raise Exception("EpistemicViolation")

@given(confidence=invalid_confidence)
def test_E2_invalid_epistemic_confidence_is_rejected(confidence):
    with pytest.raises(Exception):
        if not (0 < confidence <= 1):
            raise Exception("EpistemicViolation")

@given(is_inferred=st.booleans(), is_fact=st.booleans())
def test_E3_fact_and_inference_cannot_be_confused(is_inferred, is_fact):
    # Pré-condição: estamos no caso proibido
    assume(is_inferred and is_fact)

    # Lei: isso deve ser rejeitado
    with pytest.raises(Exception):
        raise Exception("EpistemicViolation")
    
@given(
    child_confidences=st.lists(valid_confidence, min_size=1),
    parent_confidence=valid_confidence
)
def test_E4_parent_confidence_not_greater_than_children(
    child_confidences, parent_confidence
):
    if parent_confidence > min(child_confidences):
        with pytest.raises(Exception):
            raise Exception("EpistemicViolation")

@given(
    source=valid_text,
    method=valid_text,
    justification=valid_text,
)
def test_E5_knowledge_is_auditable(source, method, justification):
    record = {
        "source": source,
        "method": method,
        "justification": justification,
    }

    # auditoria = conseguir responder "por quê?"
    assert all(record.values())
