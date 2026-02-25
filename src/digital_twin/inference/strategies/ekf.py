from __future__ import annotations

import math

from digital_twin.domain.snapshot import TwinSnapshot

from ..parameter import ParameterVector
from ..result import InferenceResult
from ..strategy import InferenceStrategy


class EKFStrategy(InferenceStrategy):
    """Deterministic 2D EKF over log-space latent efficiency/density parameters.

    Latent state:
      x = [log(cpu_per_workload), log(backlog_per_active_link)]^T

    Observation model:
      h(x) = [exp(x1), exp(x2)]^T

    Transition model:
      f(x) = x (random walk)

    Covariance is maintained and emitted in log-space.
    """

    _JITTER_EPSILON = 1e-9
    _MIN_POSITIVE_OBSERVATION = 1e-12

    def __init__(
        self,
        *,
        process_noise_diagonal: tuple[float, float] = (1e-4, 1e-4),
        observation_noise_diagonal: tuple[float, float] = (1e-3, 1e-3),
        initial_covariance_diagonal: tuple[float, float] = (1.0, 1.0),
    ) -> None:
        self._q11 = float(process_noise_diagonal[0])
        self._q22 = float(process_noise_diagonal[1])
        self._r11 = float(observation_noise_diagonal[0])
        self._r22 = float(observation_noise_diagonal[1])

        self._mean1 = 0.0
        self._mean2 = 0.0
        self._p11 = float(initial_covariance_diagonal[0])
        self._p12 = 0.0
        self._p21 = 0.0
        self._p22 = float(initial_covariance_diagonal[1])

        self._initialized = False
        self._last_timestamp: int | None = None
        self._latest = ParameterVector(
            values=(1.0, 1.0),
            covariance=((self._p11, self._p12), (self._p21, self._p22)),
            timestamp=0,
            strategy_id=self.name(),
        )

    def name(self) -> str:
        return "ekf"

    def initialize(self, snapshot: TwinSnapshot) -> None:
        z1, z2, _, _ = self._observations(snapshot)
        self._mean1 = math.log(max(z1, self._MIN_POSITIVE_OBSERVATION))
        self._mean2 = math.log(max(z2, self._MIN_POSITIVE_OBSERVATION))
        self._p12 = 0.0
        self._p21 = 0.0
        self._initialized = True
        self._last_timestamp = snapshot.version_counter
        self._latest = self._build_parameter_vector(snapshot.version_counter)

    def update(self, snapshot: TwinSnapshot) -> InferenceResult:
        if not self._initialized:
            self.initialize(snapshot)

        # Predict (random walk): x^- = x, P^- = P + Q
        p11 = self._p11 + self._q11
        p12 = self._p12
        p21 = self._p21
        p22 = self._p22 + self._q22

        z1, z2, active_workloads, active_links = self._observations(snapshot)

        # h(x) and Jacobian H
        hx1 = math.exp(self._mean1)
        hx2 = math.exp(self._mean2)
        h11 = hx1
        h12 = 0.0
        h21 = 0.0
        h22 = hx2

        # Innovation covariance S = HPH^T + R
        s11 = h11 * (p11 * h11 + p12 * h12) + h12 * (p21 * h11 + p22 * h12) + self._r11
        s12 = h11 * (p11 * h21 + p12 * h22) + h12 * (p21 * h21 + p22 * h22)
        s21 = h21 * (p11 * h11 + p12 * h12) + h22 * (p21 * h11 + p22 * h12)
        s22 = h21 * (p11 * h21 + p12 * h22) + h22 * (p21 * h21 + p22 * h22) + self._r22

        inv_s11, inv_s12, inv_s21, inv_s22 = self._invert_2x2_with_jitter(s11, s12, s21, s22)

        # Kalman gain K = P H^T S^-1
        # A = P H^T
        a11 = p11 * h11 + p12 * h12
        a12 = p11 * h21 + p12 * h22
        a21 = p21 * h11 + p22 * h12
        a22 = p21 * h21 + p22 * h22

        k11 = a11 * inv_s11 + a12 * inv_s21
        k12 = a11 * inv_s12 + a12 * inv_s22
        k21 = a21 * inv_s11 + a22 * inv_s21
        k22 = a21 * inv_s12 + a22 * inv_s22

        # Mean update
        innovation1 = z1 - hx1
        innovation2 = z2 - hx2
        self._mean1 = self._mean1 + k11 * innovation1 + k12 * innovation2
        self._mean2 = self._mean2 + k21 * innovation1 + k22 * innovation2

        # Joseph covariance update: P = (I-KH)P(I-KH)^T + KRK^T
        m11 = 1.0 - (k11 * h11 + k12 * h21)
        m12 = -(k11 * h12 + k12 * h22)
        m21 = -(k21 * h11 + k22 * h21)
        m22 = 1.0 - (k21 * h12 + k22 * h22)

        mp11 = m11 * p11 + m12 * p21
        mp12 = m11 * p12 + m12 * p22
        mp21 = m21 * p11 + m22 * p21
        mp22 = m21 * p12 + m22 * p22

        pnew11 = mp11 * m11 + mp12 * m12
        pnew12 = mp11 * m21 + mp12 * m22
        pnew21 = mp21 * m11 + mp22 * m12
        pnew22 = mp21 * m21 + mp22 * m22

        krkt11 = (k11 * self._r11) * k11 + (k12 * self._r22) * k12
        krkt12 = (k11 * self._r11) * k21 + (k12 * self._r22) * k22
        krkt21 = (k21 * self._r11) * k11 + (k22 * self._r22) * k12
        krkt22 = (k21 * self._r11) * k21 + (k22 * self._r22) * k22

        self._p11 = pnew11 + krkt11
        self._p12 = pnew12 + krkt12
        self._p21 = pnew21 + krkt21
        self._p22 = pnew22 + krkt22

        # Symmetrize + deterministic diagonal floor
        offdiag = 0.5 * (self._p12 + self._p21)
        self._p12 = offdiag
        self._p21 = offdiag
        if self._p11 < self._JITTER_EPSILON:
            self._p11 = self._JITTER_EPSILON
        if self._p22 < self._JITTER_EPSILON:
            self._p22 = self._JITTER_EPSILON

        self._last_timestamp = snapshot.version_counter
        self._latest = self._build_parameter_vector(snapshot.version_counter)

        metadata = {
            "active_workloads": float(active_workloads),
            "active_links": float(active_links),
            "z1_obs": z1,
            "z2_obs": z2,
        }
        return InferenceResult(parameter_vector=self._latest, metadata=metadata)

    def get_parameters(self) -> ParameterVector:
        return self._latest

    def _build_parameter_vector(self, timestamp: int) -> ParameterVector:
        return ParameterVector(
            values=(math.exp(self._mean1), math.exp(self._mean2)),
            covariance=((self._p11, self._p12), (self._p21, self._p22)),
            timestamp=timestamp,
            strategy_id=self.name(),
        )

    def _observations(self, snapshot: TwinSnapshot) -> tuple[float, float, int, int]:
        active_workloads = snapshot.active_workload_count
        active_links = snapshot.active_link_count

        z1 = snapshot.total_cpu_usage / float(max(1, active_workloads))
        z2 = snapshot.total_backlog / float(max(1, active_links))

        z1 = max(z1, self._MIN_POSITIVE_OBSERVATION)
        z2 = max(z2, self._MIN_POSITIVE_OBSERVATION)
        return z1, z2, active_workloads, active_links

    def _invert_2x2_with_jitter(self, a11: float, a12: float, a21: float, a22: float) -> tuple[float, float, float, float]:
        det = a11 * a22 - a12 * a21
        if abs(det) <= self._JITTER_EPSILON:
            a11 += self._JITTER_EPSILON
            a22 += self._JITTER_EPSILON
            det = a11 * a22 - a12 * a21

        inv_det = 1.0 / det
        return a22 * inv_det, -a12 * inv_det, -a21 * inv_det, a11 * inv_det
