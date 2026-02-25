import pytest

from digital_twin.inference.contracts import validate_parameter_vector
from digital_twin.inference.parameter import ParameterVector


def test_validate_parameter_vector_rejects_non_psd_covariance() -> None:
    vector = ParameterVector(
        values=(1.0, 2.0),
        covariance=((1.0, 0.0), (0.0, -1.0)),
        timestamp=1,
        strategy_id="s",
    )

    with pytest.raises(ValueError, match="positive semidefinite"):
        validate_parameter_vector(vector)


def test_validate_parameter_vector_accepts_psd_covariance() -> None:
    vector = ParameterVector(
        values=(1.0, 2.0),
        covariance=((1.0, 0.2), (0.2, 1.0)),
        timestamp=1,
        strategy_id="s",
    )

    validate_parameter_vector(vector)
