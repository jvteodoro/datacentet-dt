from __future__ import annotations

from typing import Optional

from digital_twin.application.ports.snapshot_store import SnapshotStore
from digital_twin.domain.snapshot import TwinSnapshot


class InMemorySnapshotStore(SnapshotStore):
    def __init__(self) -> None:
        self._latest: Optional[TwinSnapshot] = None

    def save(self, snapshot: TwinSnapshot) -> None:
        self._latest = snapshot

    def load_latest(self) -> Optional[TwinSnapshot]:
        return self._latest
