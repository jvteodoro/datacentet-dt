import pytest

from domain.core.snapshot import Snapshot, SnapshotInvariantViolation


def test_Hierarchy_noop_does_not_fail():
    with pytest.raises(SnapshotInvariantViolation, match="SN5"):
        Snapshot(
            observables=[],
            state_vector=None,
            parameters=[],
        )
