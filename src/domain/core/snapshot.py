"""
Snapshot — Domain Core Object (BASELINE v1.2)

Congela um instante epistemológico do Digital Twin.

Um Snapshot:
- é IMUTÁVEL
- é AUTOCONTIDO
- não executa inferência
- não aplica contratos
- apenas DECLARA fatos e relações

Ele é a única entrada válida para o Validator.
"""

from copy import deepcopy
from typing import List, Dict, Any, Optional
import numpy as np

from domain.core.observable import Observable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable


class SnapshotInvariantViolation(Exception):
    """
    Violação de invariante estrutural do Snapshot.

    Indica erro de construção do estado congelado,
    nunca erro operacional.
    """
    pass


class Snapshot:
    """
    Snapshot (Design by Contract).

    Representa uma hipótese COMPLETA e IMUTÁVEL do sistema
    em um instante lógico único.

    Ele contém:
    - metadados estruturais (software)
    - estado e observações (modelo)
    - parâmetros inferidos
    - possíveis filhos hierárquicos

    Ele NÃO:
    - lembra passado
    - infere futuro
    - valida contratos
    """

    def __init__(
        self,
        *,
        observables: List[Observable] | List[Dict[str, Any]],
        state_vector: Optional[StateVector] | Optional[Dict[str, Any]],
        identifiables: Optional[List[Identifiable] | List[Dict[str, Any]]] = None,
        parameters: Optional[List[Identifiable] | List[Dict[str, Any]]] = None,
        children: Optional[List["Snapshot"]] = None,

        # Metadados estruturais (Software Contract)
        component_id: str = "unknown",
        component_type: str = "unknown",
        name: str = "Component",
        version: str = "0.0.0",
        declared_invariants: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
    ):
        # -------------------------------------------------
        # Pré-condições estruturais básicas
        # -------------------------------------------------

        if not isinstance(observables, list):
            raise SnapshotInvariantViolation("SN1: observables must be list")

        if state_vector is not None and not isinstance(state_vector, (StateVector, dict)):
            raise SnapshotInvariantViolation("SN2: state_vector must be StateVector, dict or None")

        if identifiables is not None and parameters is not None:
            raise SnapshotInvariantViolation(
                "SN3: use either identifiables or parameters, not both"
            )

        parameters_or_identifiables = (
            identifiables if identifiables is not None else parameters
        )

        if parameters_or_identifiables is None:
            parameters_or_identifiables = []

        if not isinstance(parameters_or_identifiables, list):
            raise SnapshotInvariantViolation("SN3: identifiables must be list")

        if children is not None and not isinstance(children, list):
            raise SnapshotInvariantViolation("SN4: children must be list or None")

        if not observables and state_vector is None:
            raise SnapshotInvariantViolation("SN5: snapshot requires observables or state")

        if observables and not all(
            isinstance(o, (Observable, dict)) for o in observables
        ):
            raise SnapshotInvariantViolation("SN6: invalid observable type")

        if parameters_or_identifiables and not all(
            isinstance(p, (Identifiable, dict)) for p in parameters_or_identifiables
        ):
            raise SnapshotInvariantViolation("SN7: invalid identifiable type")

        if children:
            for c in children:
                if not isinstance(c, Snapshot):
                    raise SnapshotInvariantViolation("SN8: children must be Snapshot instances")

        # -------------------------------------------------
        # Coerência temporal GLOBAL
        # -------------------------------------------------
        # Todos os elementos devem pertencer ao MESMO instante lógico

        timestamps = []

        normalized_observables = [
            o.to_dict() if isinstance(o, Observable) else dict(o)
            for o in observables
        ]

        normalized_state_vector = (
            state_vector.to_dict() if isinstance(state_vector, StateVector) else state_vector
        )

        normalized_identifiables = [
            p.to_dict() if isinstance(p, Identifiable) else dict(p)
            for p in parameters_or_identifiables
        ]

        timestamps.extend(o["timestamp"] for o in normalized_observables)

        if normalized_state_vector:
            timestamps.append(normalized_state_vector["timestamp"])

        timestamps.extend(p["timestamp"] for p in normalized_identifiables)

        if children:
            timestamps.extend(c.timestamp for c in children)

        if len(set(timestamps)) != 1:
            raise SnapshotInvariantViolation("SN9: all components must share the same timestamp")

        self._timestamp = timestamps[0]

        # -------------------------------------------------
        # Metadados estruturais (imutáveis)
        # -------------------------------------------------

        self._component_id = component_id
        self._component_type = component_type
        self._name = name
        self._version = version
        self._declared_invariants = list(declared_invariants or [])
        self._dependencies = list(dependencies or [])

        # -------------------------------------------------
        # Conteúdo epistemológico (imutável)
        # -------------------------------------------------

        self._observables = normalized_observables
        self._state_vector = normalized_state_vector
        self._identifiables = normalized_identifiables
        self._children = list(children) if children else []

        # Selo final de imutabilidade
        self._sealed = True

    # -------------------------------------------------
    # Acesso somente leitura
    # -------------------------------------------------

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def observables(self) -> List[Dict]:
        return deepcopy(self._observables)

    @property
    def state_vector(self) -> Dict[str, Any] | None:
        return deepcopy(self._state_vector)

    @property
    def identifiables(self) -> List[Dict]:
        return deepcopy(self._identifiables)

    @property
    def parameters(self) -> List[Dict]:
        """
        Alias de compatibilidade para o nome legado.
        """
        return deepcopy(self._identifiables)

    @property
    def children(self) -> List["Snapshot"]:
        return list(self._children)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self._timestamp,
            "observables": deepcopy(self._observables),
            "state_vector": deepcopy(self._state_vector),
            "identifiables": deepcopy(self._identifiables),
            "parameters": deepcopy(self._identifiables),
            "children": [child.to_dict() for child in self._children],
            "software": self.to_software_view(),
        }

    # -------------------------------------------------
    # Imutabilidade forte
    # -------------------------------------------------

    def __setattr__(self, key, value):
        if hasattr(self, "_sealed") and self._sealed:
            raise SnapshotInvariantViolation("SN0: snapshot is immutable after creation")
        super().__setattr__(key, value)

    # -------------------------------------------------
    # Views para contratos
    # -------------------------------------------------

    def to_software_view(self) -> Dict[str, Any]:
        """
        Software View — Structural Projection

        Declara APENAS metadados estruturais.
        Nenhum dado científico aparece aqui.
        """
        return {
            "component_id": self._component_id,
            "component_type": self._component_type,
            "name": self._name,
            "version": self._version,
            "declared_invariants": list(self._declared_invariants),
            "dependencies": list(self._dependencies),
        }

    def to_temporal_view(self) -> Dict[str, Any]:
        """
        Temporal View — Causal Projection

        Declara relações temporais explícitas,
        sem inferência de causalidade.
        """
        return {
            "timestamp": self._timestamp,
            "previous_timestamp": None,
            "input_timestamps": [o['timestamp'] for o in self._observables],
            "state_timestamp": self._state_vector['timestamp'] if self._state_vector else None,
        }

    def to_statistical_view(self) -> Dict[str, Any]:
        """
        Statistical View — Uncertainty Projection

        Declara incertezas SEM assumir distribuição.
        """
        parent_variance = (
            float(np.trace(self._state_vector['covariance']))
            if self._state_vector is not None
            else None
        )

        child_variances = [
            o['uncertainty']
            for o in self._observables
            if o['uncertainty'] is not None
        ] or None

        confidences_indetifiables = [
            p['confidence']
            for p in self._identifiables
        ]
        
        confidences_observables = [
            p['confidence'] for p in self._observables
        ]
        confidences = confidences_indetifiables.append(confidences_observables)
        return {
            "estimate": bool(self._state_vector or self._identifiables),
            "uncertainty": parent_variance,
            "covariance": self._state_vector['covariance'] if self._state_vector else None,
            "confidence": min(confidences) if confidences else None,
            "child_variances": child_variances,
            "parent_variance": parent_variance,
        }

    def to_epistemic_view(self) -> List[Dict[str, Any]]:
        """
        Epistemic View — Knowledge Projection

        Produz registros explícitos de conhecimento,
        sem promover estado automaticamente.
        """
        records: List[Dict[str, Any]] = []

        for obs in self._observables:
            records.append({
                "value": obs['value'],
                "source": obs['source'],
                "method": "direct observation",
                "justification": "sensor measurement",
                "confidence": None,
                "epistemic_type": "observed",
            })

        for param in self._identifiables:
            records.append({
                "value": param['estimated_value'],
                "source": "parameter_identifier",
                "method": param['method'],
                "justification": f"inferred from {param['support']}",
                "confidence": param['confidence'],
                "epistemic_type": "inferred",
                "child_confidences": [
                    o['uncertainty'] for o in self._observables if o['uncertainty'] is not None
                ] or None,
            })

        return records

    def to_model_view(self) -> Dict[str, Any]:
        """
        Model View — State Consistency Projection

        Declara relações entre estado, observações
        e incerteza SEM inferência.
        """

        state_value = (
            [v['value'] for v in self._state_vector['variables']]
            if self._state_vector else None
        )

        state_variance = (
            float(np.trace(self._state_vector['covariance']))
            if self._state_vector else None
        )

        observation_value = (
            self._observables[0]['value']
            if self._observables else None
        )

        observation_variance = (
            self._observables[0]['uncertainty']
            if self._observables else None
        )

        return {
            "state_value": state_value,
            "state_variance": state_variance,
            "previous_state_variance": None,

            "observations": list(self._observables),
            "observation_value": observation_value,
            "observation_variance": observation_variance,

            "has_new_data": bool(self._observables),

            "previous_entropy": None,
            "new_entropy": None,
            "has_inputs": bool(self._observables),

            "expose_as_knowledge": False,
            "exposed_value": None,
            "confidence": None,
        }


    def to_hierarchy_view(self) -> Dict[str, Any]:
        """
        Hierarchy View — Emergent Composition Projection

        Declara relações entre este snapshot e seus filhos.
        """
        if not self._children:
            return {
                "accessed_internal_fields": False,
                "parent_timestamp": self.timestamp,
                "child_timestamps": None,
                "parent_variance": None,
                "child_variances": None,
                "parent_confidence": None,
                "child_confidences": None,
                "local_error": False,
                "validated": False,
                "child_failures": None,
            }

        parent_variance = (
            float(np.trace(self._state_vector['covariance']))
            if self._state_vector else None
        )

        child_variances = [
            float(np.trace(c.state_vector['covariance']))
            for c in self._children
            if c.state_vector is not None
        ] or None

        child_confidences = []
        for child in self._children:
            for rec in child.to_epistemic_view():
                if rec.get("confidence") is not None:
                    child_confidences.append(rec["confidence"])

        return {
            "accessed_internal_fields": False,
            "parent_timestamp": self.timestamp,
            "child_timestamps": [c.timestamp for c in self._children],
            "parent_variance": parent_variance,
            "child_variances": child_variances,
            "parent_confidence": None,
            "child_confidences": child_confidences or None,
            "local_error": False,
            "validated": False,
            "child_failures": [False for _ in self._children],
        }
