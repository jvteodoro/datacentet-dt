import pytest

from domain.core.identifiable import Identifiable, IdentifiableInvariantViolation
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


class SnapshotEpistemicPayloadFactory(Snapshot):
    """Factory de teste para injetar payload epistêmico sem mutar objetos de domínio.

    Precedência documentada:
    1) Invariantes estruturais (ex.: I7 imutabilidade em ``Identifiable``)
       são checados na criação/mutação dos objetos de domínio.
    2) Invariantes semânticos epistêmicos (ex.: E3) são checados no validator
       sobre a view serializada de conhecimento.
    """

    def __init__(self, epistemic_records: list[dict]):
        self._epistemic_records = list(epistemic_records)

    def to_software_view(self):
        return {
            "component_id": "validator-test",
            "component_type": "test",
            "name": "validator-test",
            "version": "1.0.0",
            "declared_invariants": ["I7", "E3"],
            "dependencies": [],
        }

    def to_temporal_view(self):
        return {
            "timestamp": 0,
            "previous_timestamp": None,
            "input_timestamps": [0],
            "state_timestamp": None,
        }

    def to_statistical_view(self):
        return {
            "estimate": False,
            "uncertainty": None,
            "covariance": None,
            "confidence": None,
            "child_variances": None,
            "parent_variance": None,
        }

    def to_epistemic_view(self):
        return list(self._epistemic_records)

    def to_model_view(self):
        return {
            "state_value": None,
            "state_variance": None,
            "previous_state_variance": None,
            "observations": [{"value": 1.0}],
            "observation_value": 1.0,
            "observation_variance": None,
            "has_new_data": True,
            "previous_entropy": None,
            "new_entropy": None,
            "has_inputs": True,
            "expose_as_knowledge": False,
            "exposed_value": None,
            "confidence": None,
        }

    def to_hierarchy_view(self):
        return {
            "accessed_internal_fields": False,
            "parent_timestamp": 0,
            "child_timestamps": None,
            "children": [],
        }


def test_I7_identifiable_is_immutable_after_creation():
    param = Identifiable(
        name="gain",
        estimated_value=2.0,
        uncertainty=0.1,
        timestamp=0,
        method="fit",
        support=["y"],
    )

    with pytest.raises(IdentifiableInvariantViolation, match="I7"):
        param._is_fact = True  # type: ignore[attr-defined]


def test_E3_identifiable_cannot_be_fact_without_violating_I7_first():
    snap = SnapshotEpistemicPayloadFactory(
        epistemic_records=[
            {
                "value": 2.0,
                "source": "parameter_identifier",
                "method": "fit",
                "justification": "inferred from ['y']",
                "confidence": 0.9,
                "epistemic_type": "inferred",
                "is_fact": True,
            }
        ]
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Epistemic[0]" in result.violations
    assert any(
        "E3: inferred knowledge cannot be treated as fact" in msg
        for msg in result.violations["Epistemic[0]"]
    )
