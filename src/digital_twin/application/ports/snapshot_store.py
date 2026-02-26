from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from digital_twin.domain.snapshot import TwinSnapshot


class SnapshotStore(ABC):
    @abstractmethod
    def save(self, snapshot: TwinSnapshot, **kwargs: object) -> None:
        """Persist the latest immutable twin snapshot."""

    @abstractmethod
    def load_latest(self, **kwargs: object) -> Optional[TwinSnapshot]:
        """Load the latest persisted immutable snapshot if it exists."""
