"""
IdentifiableRegistry — Domain Internal Component (BASELINE v1.0)

Gerencia parâmetros inferidos e suas versões ativas.
"""

from typing import Dict, Optional, List

from domain.core.identifiable import Identifiable


class IdentifiableRegistryViolation(Exception):
    """
    Violação de contrato do IdentifiableRegistry.
    """
    pass


class IdentifiableRegistry:
    """
    Registry operacional de Identifiables.

    NÃO:
    - identifica parâmetros
    - valida ciência
    - persiste dados
    """

    def __init__(self):
        # Mapa: name -> Identifiable ativo
        self._active: Dict[str, Identifiable] = {}

    # -------------------------------------------------
    # Registro
    # -------------------------------------------------

    def register(self, param: Identifiable) -> None:
        if not isinstance(param, Identifiable):
            raise IdentifiableRegistryViolation(
                "IR1: only Identifiable instances can be registered"
            )

        name = param.name

        if name not in self._active:
            self._active[name] = param
            return

        current = self._active[name]

        # IR3: não permitir sobrescrita por versão mais antiga
        if param.timestamp < current.timestamp:
            return

        # Atualiza versão ativa
        self._active[name] = param

    # -------------------------------------------------
    # Consultas
    #-------------------------------------------------

    def get_current(self, name: str) -> Optional[Identifiable]:
        if not isinstance(name, str):
            raise IdentifiableRegistryViolation(
                "IR2: name must be string"
            )

        return self._active.get(name)

    def get_all_current(self) -> List[Identifiable]:
        return list(self._active.values())

    def latest_timestamp(self) -> Optional[int]:
        if not self._active:
            return None
        return max(p.timestamp for p in self._active.values())