"""
InternalStateModel — Domain Orchestrator (BASELINE v1.0)

Coordena inferência de estado e parâmetros.
"""

from typing import Optional

from domain.core.observable import Observable
from domain.core.observable_registry import ObservableRegistry
from domain.core.identifiable_registry import IdentifiableRegistry
from domain.core.snapshot import Snapshot


class InternalStateModelViolation(Exception):
    """
    Violação de contrato do InternalStateModel.
    """
    pass


class InternalStateModel:
    def __init__(
        self,
        *,
        observable_registry: ObservableRegistry,
        identifiable_registry: IdentifiableRegistry,
        state_estimator,
        parameter_identifier,
        component_id: str = "unknown",
        component_type: str = "unknown",
        name: str = "Component",
        version: str = "0.0.0",
        declared_invariants: list[str] | None = None,
        dependencies: list[str] | None = None,
    ):
        self._obs_registry = observable_registry
        self._id_registry = identifiable_registry
        self._state_estimator = state_estimator
        self._parameter_identifier = parameter_identifier
        self._component_id = component_id
        self._component_type = component_type
        self._name = name
        self._version = version
        self._declared_invariants = list(declared_invariants or [])
        self._dependencies = list(dependencies or [])

    # -------------------------------------------------
    # Entrada de dados
    # -------------------------------------------------

    def ingest_observation(self, observable: Observable) -> None:
        self._obs_registry.register(observable)

    # -------------------------------------------------
    # Passo de inferência
    # -------------------------------------------------

    def step(self, timestamp: int) -> Optional[Snapshot]:
        observables = self._obs_registry.get_at(timestamp)

        if not observables:
            return None

        # Inferência de estado
        state_vector = self._state_estimator.estimate(observables)

        # Identificação de parâmetros (opcional)
        params = self._parameter_identifier.identify(state_vector)

        for p in params:
            self._id_registry.register(p)

        # Construção de snapshot (respeita validações de metadados)
        return Snapshot(
            observables=observables,
            state_vector=state_vector,
            identifiables=self._id_registry.get_all_current(),
            component_id=self._component_id,
            component_type=self._component_type,
            name=self._name,
            version=self._version,
            declared_invariants=list(self._declared_invariants),
            dependencies=list(self._dependencies),
        )
