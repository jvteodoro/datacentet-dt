import pytest

from domain.contracts.hierarchy import HierarchyContract, HierarchyInvariantViolation
from domain.contracts.temporal import TemporalContract, TemporalViolation


def test_temporal_rule_allows_equal_timestamp_for_causality_boundary():
    contract = TemporalContract()
    contract.validate(
        {
            "timestamp": 10,
            "input_timestamps": [10],
        }
    )


def test_temporal_rule_rejects_strict_future_timestamp():
    contract = TemporalContract()

    with pytest.raises(TemporalViolation, match="T3: future data is not causally admissible"):
        contract.validate(
            {
                "timestamp": 10,
                "input_timestamps": [11],
            }
        )


def test_h2_parent_child_visibility_allows_equal_timestamp():
    contract = HierarchyContract()
    contract.validate(
        {
            "accessed_internal_fields": False,
            "parent_timestamp": 10,
            "child_timestamps": [10],
            "local_error": False,
            "validated": True,
            "child_failures": [False],
        }
    )


def test_h2_parent_child_visibility_rejects_child_future():
    contract = HierarchyContract()

    with pytest.raises(HierarchyInvariantViolation, match="H2: parent temporal context precedes child context"):
        contract.validate(
            {
                "accessed_internal_fields": False,
                "parent_timestamp": 10,
                "child_timestamps": [11],
                "local_error": False,
                "validated": True,
                "child_failures": [False],
            }
        )
