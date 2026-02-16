"""
Energy Power Feed Digital Twin — DEMO COMPONENT

Este módulo implementa um Digital Twin mínimo do subsistema
de energia de um data center (power feed).

Camada:
- Application

Este código:
- NÃO define leis do domínio
- NÃO implementa contratos
- NÃO assume hardware específico
- NÃO executa controle automático

Ele demonstra COMO USAR o core científico do Digital Twin.
"""

from typing import Dict, List
import numpy as np
from psu_mock import psu_mock

# ----------------------------
# Importações do domínio
# ----------------------------

from domain.core.observable import Observable
from domain.core.identifiable import Identifiable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.snapshot import Snapshot

from domain.validation.validator import Validator


# ============================================================
# Energy Power Feed Twin (Application Component)
# ============================================================

class EnergyPowerFeedTwin:
    """
    Digital Twin do subsistema de alimentação elétrica.

    Responsabilidades:
    - Receber observações elétricas
    - Manter estado interno (hipótese)
    - Inferir parâmetros
    - Gerar snapshots epistemológicos
    - Validar cientificamente o snapshot

    Este componente:
    - NÃO expõe estado interno
    - NÃO executa controle
    - NÃO aprende automaticamente
    """

    def __init__(self, *, component_name: str, version: str):
        self._name = component_name
        self._version = version
        self._validator = Validator()

        # Estado interno mínimo (hipótese persistente)
        self._last_state_vector: StateVector | None = None
        self._last_timestamp: int | None = None

    # --------------------------------------------------------
    # Interface pública
    # --------------------------------------------------------

    def step(self, *, voltage_v: float, current_a: float, timestamp: int) -> Snapshot:
        """
        Executa um passo lógico do Digital Twin.

        Entrada:
        - voltage_v: tensão observada [V]
        - current_a: corrente observada [A]
        - timestamp: tempo lógico

        Saída:
        - Snapshot validado cientificamente
        """

        # ----------------------------
        # 1. Observáveis (medição)
        # ----------------------------

        voltage = Observable(
            name="input_voltage",
            value=voltage_v,
            uncertainty=1.0,
            confidence=1.0,
            timestamp=timestamp,
            source="voltage_sensor",
        )

        current = Observable(
            name="input_current",
            value=current_a,
            uncertainty=0.2,
            confidence=1.0,
            timestamp=timestamp,
            source="current_sensor",
        )

        observables = [voltage, current]

        # ----------------------------
        # 2. Estado interno (hipótese)
        # ----------------------------

        estimated_power = voltage_v * current_a  # W
        power_uncertainty = abs(estimated_power) * 0.02  # 2%

        power_state = StateVariable(
            name="active_power",
            value=estimated_power,
            uncertainty=power_uncertainty,
            timestamp=timestamp,
        )

        state_vector = StateVector(
            variables=[power_state],
            covariance=np.array([[power_uncertainty**2]]),
        )

        self._last_state_vector = state_vector
        self._last_timestamp = timestamp

        # ----------------------------
        # 3. Parâmetro identificável
        # ----------------------------

        efficiency = Identifiable(
            name="power_efficiency",
            estimated_value=0.92,
            uncertainty=0.03,
            confidence=0.1,
            timestamp=timestamp,
            method="static_assumption",
            support=["input_voltage", "input_current"],
        )

        parameters = [efficiency]

        # ----------------------------
        # 4. Snapshot epistemológico
        # ----------------------------

        snapshot = Snapshot(
            observables=observables,
            state_vector=state_vector,
            identifiables=parameters,
            component_id="a12b",
            component_type='energy',
            name='energy_power_feed',
            version='1.0.0',
            declared_invariants=['SW1'],
            dependencies=[]
        )
        #print(snapshot.to_statistical_view())
        # ----------------------------
        # 5. Validação científica
        # ----------------------------

        result = self._validator.validate(snapshot=snapshot)

        if not result.is_valid:
            raise RuntimeError(
                f"Snapshot inválido:\n{result.violations}"
            )

        return snapshot


# ============================================================
# Demonstração de uso
# ============================================================

def run_demo():
    """
    Executa uma demonstração simples do Digital Twin.
    """

    twin = EnergyPowerFeedTwin(
        component_name="energy_power_feed",
        version="1.0.0",
    )

    snapshot = twin.step(
        voltage_v=230.0,
        current_a=10.0,
        timestamp=100,
    )

    #lsprint("\n=== SNAPSHOT ===")
    #print(snapshot.to_dict())

    print("\n=== SOFTWARE VIEW ===")
    print(snapshot.to_software_view())

    print("\n=== TEMPORAL VIEW ===")
    print(snapshot.to_temporal_view())

    print("\n=== STATISTICAL VIEW ===")
    print(snapshot.to_statistical_view())

    print("\n=== EPISTEMIC VIEW ===")
    print(snapshot.to_epistemic_view())

    print("\n=== MODEL VIEW ===")
    print(snapshot.to_model_view())


if __name__ == "__main__":
    run_demo()
