import numpy as np
import pytest

from domain.contracts.statistical import StatisticalContract, StatisticalViolation
from domain.core.covariance_utils import PSD_EIGENVALUE_TOLERANCE


def test_S2_accepts_psd_with_small_negative_eigenvalue_within_tolerance():
    cov = np.array([[1.0, 0.0], [0.0, -1e-10]])

    StatisticalContract().validate({"covariance": cov})


def test_S2_rejects_psd_when_eigenvalue_below_tolerance():
    cov = np.array([[1.0, 0.0], [0.0, PSD_EIGENVALUE_TOLERANCE - 1e-6]])

    with pytest.raises(StatisticalViolation, match="positive semidefinite"):
        StatisticalContract().validate({"covariance": cov})
