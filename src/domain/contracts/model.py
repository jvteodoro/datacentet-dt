"""
Model Domain Contract — BASELINE v1.0 (REFINED)

Este módulo define as LEIS COMPOSTAS do Domain Level.

Ele conecta:
- observações
- incerteza
- conhecimento
- tempo

SEM assumir:
- filtros
- modelos físicos
- inferência concreta

Pergunta respondida:
→ "Dado um snapshot de estado, ele é cientificamente consistente?"
"""

from typing import Any, Dict, List
import numpy as np


class ModelInvariantViolation(Exception):
    """
    Violação de invariante de modelo do Domain Level.

    Indica inconsistência científica EMERGENTE,
    mesmo que contratos primários estejam localmente válidos.
    """
    pass


class ModelContract:
    """
    Contrato de modelo do Domain Level.

    Este contrato:
    - é composto
    - é puro
    - é determinístico
    - opera exclusivamente sobre snapshots
    - não mantém estado
    """

    # ------------------------------------------------------------------
    # Entrada esperada
    # ------------------------------------------------------------------
    # snapshot: Dict[str, Any]
    #
    # Campos semanticamente esperados:
    # - state_value
    # - state_variance
    # - observations: List[Any]
    # - observation_value
    # - observation_variance
    # - previous_state_variance
    # - has_new_data: bool
    # - previous_entropy
    # - new_entropy
    # - has_inputs: bool
    # - exposed_value
    # - expose_as_knowledge: bool
    # - confidence
    #
    # O contrato valida RELAÇÕES, não estruturas rígidas.
    # ------------------------------------------------------------------

    def validate(self, snapshot: Dict[str, Any]) -> None:
        """
        Valida o snapshot contra os invariantes de modelo M1–M3.

        Método:
        - puro
        - determinístico
        - sem efeitos colaterais

        Falha explicitamente com ModelInvariantViolation.
        """

        self._validate_M1_state_observation(snapshot)
        self._validate_M2_information_creation(snapshot)
        self._validate_M3_state_vs_knowledge(snapshot)

    # ------------------------------------------------------------------
    # M1 — Consistência Estado–Observação
    # ------------------------------------------------------------------

    def _validate_M1_state_observation(self, snapshot: Dict[str, Any]) -> None:
        """
        M1 — State–Observation Consistency

        Lei composta:
        - Um estado deve ser estatisticamente compatível
          com as observações que o suportam
        - Um estado não pode ser autojustificado
        """

        observations = snapshot.get("observations")
        if not observations:
            raise ModelInvariantViolation(
                "M1: state without observational support is invalid"
            )

        required = {
            "state_value",
            "observation_value",
            "observation_variance",
        }
        if not required.issubset(snapshot):
            return

        state_value = snapshot["state_value"]
        obs_value = snapshot["observation_value"]
        variance = snapshot["observation_variance"]

        if variance <= 0:
            raise ModelInvariantViolation("M1: variance must be positive")

        residual = obs_value - state_value
        sigma = np.sqrt(variance)
        normalized = abs(residual / sigma)

        limit = snapshot.get("compatibility_limit", 10.0)

        if normalized > limit:
            raise ModelInvariantViolation(
                "M1: state incompatible with supporting observation"
            )

    # ------------------------------------------------------------------
    # M2 — Não criação espúria de informação
    # ------------------------------------------------------------------

    def _validate_M2_information_creation(self, snapshot: Dict[str, Any]) -> None:
        """
        M2 — No Spurious Information Creation

        Lei:
        Informação NÃO pode ser criada sem entrada externa.
        """

        prev_var = snapshot.get("previous_state_variance")
        new_var = snapshot.get("state_variance")
        has_new_data = snapshot.get("has_new_data")

        if (
            prev_var is not None
            and new_var is not None
            and has_new_data is False
            and new_var < prev_var
        ):
            raise ModelInvariantViolation(
                "M2: uncertainty reduction without new data"
            )

        prev_entropy = snapshot.get("previous_entropy")
        new_entropy = snapshot.get("new_entropy")
        has_inputs = snapshot.get("has_inputs")

        if (
            prev_entropy is not None
            and new_entropy is not None
            and has_inputs is False
            and new_entropy < prev_entropy
        ):
            raise ModelInvariantViolation(
                "M2: information gain without inputs is invalid"
            )

    # ------------------------------------------------------------------
    # M3 — Separação Estado vs Conhecimento
    # ------------------------------------------------------------------

    def _validate_M3_state_vs_knowledge(self, snapshot: Dict[str, Any]) -> None:
        """
        M3 — State vs Knowledge Separation

        Lei:
        Estado interno NÃO é conhecimento exposto por padrão.
        """

        if snapshot.get("expose_as_knowledge") is True:
            if snapshot.get("confidence") is None:
                raise ModelInvariantViolation(
                    "M3: exposed knowledge requires explicit confidence"
                )

            if snapshot.get("state_value") == snapshot.get("exposed_value"):
                raise ModelInvariantViolation(
                    "M3: state and exposed knowledge are identical without justification"
                )
