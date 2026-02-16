from domain.core.snapshot import Snapshot
from domain.validation.validator import Validator


def test_Hierarchy_noop_does_not_fail():
    snap = Snapshot(
        observables=[],
        state_vector=None,
        parameters=[],
    )

    # Snapshot inválido por outros motivos,
    # mas hierarquia não deve gerar falha própria
    result = Validator().validate(snapshot=snap)

    assert "Hierarchy" not in result.violations