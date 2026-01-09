"""
Snapshot — Domain Core Object (BASELINE v1.1)

Congela um instante epistemológico do Digital Twin.
"""

from typing import List, Dict, Any, Optional
from domain.core.observable import Observable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable


class SnapshotInvariantViolation(Exception):
    """
    Violação de invariante do Snapshot.
    """
    pass


class Snapshot:
    """
    Snapshot (Design by Contract).

    Representa uma hipótese completa do sistema
    em um instante lógico único.
    """

    def __init__(
        self,
        *,
        observables: List[Observable],
        state_vector: Optional[StateVector],
        identifiables: List[Identifiable],
        children: Optional[List["Snapshot"]] = None,
    ):
        # -------------------------
        # Pré-condições estruturais
        # -------------------------

        if not isinstance(observables, list):
            raise SnapshotInvariantViolation("SN1: observables must be list")

        if state_vector is not None and not isinstance(state_vector, StateVector):
            raise SnapshotInvariantViolation(
                "SN2: state_vector must be StateVector or None"
            )

        if not isinstance(identifiables, list):
            raise SnapshotInvariantViolation("SN3: identifiables must be list")

        if children is not None and not isinstance(children, list):
            raise SnapshotInvariantViolation("SN4: children must be list or None")

        if not observables and state_vector is None:
            raise SnapshotInvariantViolation(
                "SN5: snapshot requires observables or state"
            )

        if observables and not all(isinstance(o, Observable) for o in observables):
            raise SnapshotInvariantViolation("SN6: invalid observable type")

        if identifiables and not all(isinstance(p, Identifiable) for p in identifiables):
            raise SnapshotInvariantViolation("SN7: invalid identifiable type")

        if children:
            for c in children:
                if not isinstance(c, Snapshot):
                    raise SnapshotInvariantViolation(
                        "SN8: children must be Snapshot instances"
                    )

        # -------------------------
        # Coerência temporal global
        # -------------------------

        timestamps = []

        if observables:
            timestamps.extend(o.timestamp for o in observables)

        if state_vector:
            timestamps.append(state_vector.timestamp)

        if identifiables:
            timestamps.extend(p.timestamp for p in identifiables)

        if children:
            timestamps.extend(c.timestamp for c in children)

        if len(set(timestamps)) != 1:
            raise SnapshotInvariantViolation(
                "SN9: all components must share the same timestamp"
            )

        self._timestamp = timestamps[0]

        # -------------------------
        # Estado interno imutável
        # -------------------------

        self._observables = list(observables)
        self._state_vector = state_vector
        self._identifiables = list(identifiables)
        self._children = list(children) if children else []

        self._sealed = True

    # -------------------------
    # Acesso somente leitura
    # -------------------------

    @property
    def observables(self) -> List[Observable]:
        return list(self._observables)

    @property
    def state_vector(self) -> Optional[StateVector]:
        return self._state_vector

    @property
    def identifiables(self) -> List[Identifiable]:
        return list(self._identifiables)

    @property
    def children(self) -> List["Snapshot"]:
        return list(self._children)

    @property
    def timestamp(self) -> int:
        return self._timestamp

    # -------------------------
    # Imutabilidade
    # -------------------------

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise SnapshotInvariantViolation(
                "SN0: snapshot is immutable after creation"
            )
        super().__setattr__(key, value)

    # -------------------------
    # Interface canônica
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Representação autocontida do snapshot.
        """
        return {
            "timestamp": self.timestamp,
            "observables": [o.to_dict() for o in self.observables],
            "state_vector": (
                self.state_vector.to_dict() if self.state_vector else None
            ),
            "identifiables": [p.to_dict() for p in self.identifiables],
            "children": [c.to_dict() for c in self.children],
        }
