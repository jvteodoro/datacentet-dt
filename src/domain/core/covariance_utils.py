"""
Utilitários para validação e normalização de matrizes de covariância.

Este módulo centraliza a regra PSD (simetria + autovalores), incluindo
uma tolerância numérica padronizada para evitar divergência entre validadores.
"""

from __future__ import annotations

import numpy as np

# Tolerância numérica contratual para autovalores de PSD.
# Valores >= -1e-9 são tratados como erro numérico de ponto flutuante.
PSD_EIGENVALUE_TOLERANCE = -1e-9


class CovarianceDomainViolation(Exception):
    """Erro de domínio para covariância inválida."""


def symmetrize_covariance(covariance: np.ndarray) -> np.ndarray:
    """
    Retorna uma versão simétrica da matriz.

    Útil em caminhos de criação/transformação para remover assimetria
    numérica residual introduzida por operações de ponto flutuante.
    """

    return (covariance + covariance.T) / 2.0


def validate_psd_covariance(
    covariance: np.ndarray,
    *,
    expected_dim: int | None = None,
    context: str = "covariance",
) -> None:
    """
    Valida se a matriz é quadrada, simétrica e semidefinida positiva.

    A semidefinição positiva usa a tolerância `PSD_EIGENVALUE_TOLERANCE`
    para absorver erro numérico próximo de zero.
    """

    if not isinstance(covariance, np.ndarray):
        raise CovarianceDomainViolation(f"{context} must be a numpy array")

    if covariance.ndim != 2:
        raise CovarianceDomainViolation(f"{context} must be a 2D matrix")

    rows, cols = covariance.shape
    if rows != cols:
        raise CovarianceDomainViolation(f"{context} must be square")

    if expected_dim is not None and covariance.shape != (expected_dim, expected_dim):
        raise CovarianceDomainViolation(
            f"{context} dimension mismatch: expected {(expected_dim, expected_dim)}, got {covariance.shape}"
        )

    if not np.allclose(covariance, covariance.T):
        raise CovarianceDomainViolation(f"{context} must be symmetric")

    eigvals = np.linalg.eigvalsh(covariance)
    if np.any(eigvals < PSD_EIGENVALUE_TOLERANCE):
        raise CovarianceDomainViolation(
            f"{context} must be positive semidefinite (eigenvalues >= {PSD_EIGENVALUE_TOLERANCE})"
        )

