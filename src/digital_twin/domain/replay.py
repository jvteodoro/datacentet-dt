from collections.abc import Iterable

from .event import DomainEvent
from .twin import DataCenterTwin



def replay_events(event_sequence: Iterable[DomainEvent]) -> DataCenterTwin:
    twin = DataCenterTwin()
    twin.replay(event_sequence)
    return twin
