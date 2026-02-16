# core/registry.py
from typing import Dict
from domain.core.observable import Observable
from domain.core.identifiable import Identifiable


class ObservableRegistry:
    def __init__(self):
        self._observables: Dict[str, Observable] = {}

    def register(self, name: str, obs: Observable) -> None:
        assert name not in self._observables
        self._observables[name] = obs

    def get(self, name: str) -> Observable:
        return self._observables[name]

    # def valid(self, at_time: float) -> dict[str, Observable]:
    #     return {
    #         k: v for k, v in self._observables.items()
    #         if v.is_valid(at_time)
    #     }
