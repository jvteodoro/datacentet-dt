import pytest

from domain.core.identifiable import Identifiable
from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_E3_identifiable_cannot_be_fact():
    param = Identifiable(
        name="gain",
        estimated_value=2.0,
        uncertainty=0.1,
        timestamp=0,
        method="fit",
        support=["y"],
    )

    # Violação artificial
    param._is_fact = True  # type: ignore

    snap = Snapshot(
        observables=[],
        state_vector=None,
        parameters=[param],
    )

    result = Validator().validate(snapshot=snap)

    assert not result.is_valid
    assert "Epistemic" in result.violations