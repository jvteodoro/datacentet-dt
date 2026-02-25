from __future__ import annotations

import math

from .parameter import ParameterVector


def validate_parameter_vector(parameter_vector: ParameterVector, previous_timestamp: int | None = None) -> None:
    """Validate epistemic parameter contracts."""
    for value in parameter_vector.values:
        if math.isnan(value) or math.isinf(value):
            raise ValueError("parameter values must be finite")

    if parameter_vector.covariance is not None:
        covariance = parameter_vector.covariance
        dim = len(parameter_vector.values)
        if len(covariance) != dim or any(len(row) != dim for row in covariance):
            raise ValueError("covariance must be square and aligned with values")

        for i in range(dim):
            for j in range(dim):
                entry = covariance[i][j]
                if math.isnan(entry) or math.isinf(entry):
                    raise ValueError("covariance must be finite")
                if covariance[i][j] != covariance[j][i]:
                    raise ValueError("covariance must be symmetric")

        if not _is_positive_semidefinite(covariance):
            raise ValueError("covariance must be positive semidefinite")

    if previous_timestamp is not None and parameter_vector.timestamp < previous_timestamp:
        raise ValueError("parameter timestamp must be monotonic")


def _is_positive_semidefinite(matrix: tuple[tuple[float, ...], ...], tolerance: float = 1e-12) -> bool:
    """Check PSD with deterministic LDL^T decomposition.

    For symmetric matrices, all D pivots in LDL^T must be non-negative.
    """

    n = len(matrix)
    if n == 0:
        return True

    lower = [[0.0] * n for _ in range(n)]
    diagonal = [0.0] * n

    for i in range(n):
        for j in range(i):
            total = matrix[i][j]
            for k in range(j):
                total -= lower[i][k] * lower[j][k] * diagonal[k]

            if abs(diagonal[j]) <= tolerance:
                if abs(total) > tolerance:
                    return False
                lower[i][j] = 0.0
            else:
                lower[i][j] = total / diagonal[j]

        pivot = matrix[i][i]
        for k in range(i):
            pivot -= (lower[i][k] ** 2) * diagonal[k]

        if pivot < -tolerance:
            return False
        diagonal[i] = 0.0 if abs(pivot) <= tolerance else pivot
        lower[i][i] = 1.0

    return True
