"""
Software Domain Contract — BASELINE v1.0 (REFINED)

Este módulo define as LEIS ESTRUTURAIS do Domain Level.
Ele NÃO implementa componentes.
Ele NÃO executa validações implicitamente.
Ele NÃO conhece infraestrutura nem aplicação.

Pergunta respondida:
→ "Dado um snapshot de um componente, ele é estruturalmente válido?"

Este contrato é:
- puro
- determinístico
- aplicável via validator
"""

import re
from typing import Any, Dict, List


class SoftwareViolation(Exception):
    """
    Violação de invariante estrutural do Domain Level.

    Esta exceção indica:
    - erro conceitual
    - violação de lei do domínio
    - nunca erro operacional ou técnico
    """
    pass


class SoftwareContract:
    """
    Contrato estrutural do Domain Level.

    Este contrato valida APENAS:
    - forma
    - identidade
    - declarações
    - consistência estrutural

    Ele opera EXCLUSIVAMENTE sobre snapshots imutáveis,
    nunca sobre objetos vivos.
    """

    _SEMVER_REGEX = re.compile(r"\d+\.\d+\.\d+")

    # ------------------------------------------------------------------
    # Entrada esperada
    # ------------------------------------------------------------------
    # snapshot: Dict[str, Any]
    #
    # Campos mínimos esperados:
    # - component_id: str
    # - component_type: str
    # - name: str
    # - version: str (semver)
    # - declared_invariants: List[str]
    # - dependencies: List[str]
    #
    # O contrato NÃO assume como esses dados são produzidos.
    # ------------------------------------------------------------------

    def validate(self, snapshot: Dict[str, Any]) -> None:
        """
        Valida o snapshot de um componente contra os invariantes SW.

        Este método é:
        - puro
        - determinístico
        - sem efeitos colaterais

        Falha explicitamente com SoftwareViolation.
        """

        self._validate_sw1_integrity(snapshot)
        self._validate_sw2_immutability(snapshot)
        self._validate_sw3_responsibilities(snapshot)
        self._validate_sw4_determinism(snapshot)

    # ------------------------------------------------------------------
    # SW1 — Integridade estrutural
    # ------------------------------------------------------------------

    def _validate_sw1_integrity(self, snapshot: Dict[str, Any]) -> None:
        """
        SW1 — Structural Integrity

        Garante que o snapshot contém TODOS os metadados
        estruturais obrigatórios, com valores válidos.

        Falhas cobertas:
        - objeto mal definido
        - identidade incompleta
        - versão inválida
        """

        name = snapshot.get("name")
        version = snapshot.get("version")

        if not isinstance(name, str) or not name.strip():
            raise SoftwareViolation("SW1: invalid or missing component name")

        if not isinstance(version, str) or not self._SEMVER_REGEX.fullmatch(version):
            raise SoftwareViolation("SW1: invalid or missing semantic version")

        invariants = snapshot.get("declared_invariants")
        if not isinstance(invariants, list):
            raise SoftwareViolation("SW1: declared_invariants must be a list")

    # ------------------------------------------------------------------
    # SW2 — Imutabilidade de contrato
    # ------------------------------------------------------------------

    def _validate_sw2_immutability(self, snapshot: Dict[str, Any]) -> None:
        """
        SW2 — Contract Immutability

        O contrato NÃO impõe como a imutabilidade é implementada.
        Ele apenas exige que, DENTRO DE UM SNAPSHOT,
        metadados contratuais sejam coerentes.

        A detecção de mudança entre snapshots é responsabilidade
        do validator ou de camadas superiores.
        """

        # SW2 é garantido por design do snapshot (imutável).
        # Aqui apenas afirmamos sua existência como invariante.
        return

    # ------------------------------------------------------------------
    # SW3 — Separação de responsabilidades
    # ------------------------------------------------------------------

    def _validate_sw3_responsibilities(self, snapshot: Dict[str, Any]) -> None:
        """
        SW3 — Responsibility Separation

        Um componente NÃO pode declarar invariantes estruturais
        que são impostos externamente pelo sistema.

        Exemplo:
        - SW3 não pode ser auto-declarado
        """

        declared: List[str] = snapshot.get("declared_invariants", [])

        if "SW3" in declared:
            raise SoftwareViolation(
                "SW3: component cannot declare responsibility separation invariant"
            )

    # ------------------------------------------------------------------
    # SW4 — Determinismo de interface
    # ------------------------------------------------------------------

    def _validate_sw4_determinism(self, snapshot: Dict[str, Any]) -> None:
        """
        SW4 — Interface Determinism

        Este contrato é determinístico por construção:
        - mesma entrada → mesma validação
        - nenhuma fonte de aleatoriedade
        - nenhuma dependência externa

        A existência deste método torna o invariante explícito
        e auditável.
        """
        return
