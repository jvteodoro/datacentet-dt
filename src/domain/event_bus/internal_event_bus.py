from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict, is_dataclass
from numbers import Real
from typing import Callable, Deque, DefaultDict, TypeAlias

from domain.events import DomainEvent

EventHandler: TypeAlias = Callable[[DomainEvent], None]


class InternalEventBus:
    """Deterministic in-memory event bus for domain-level causal propagation."""

    def __init__(self) -> None:
        self._subscribers: DefaultDict[type[DomainEvent], list[EventHandler]] = defaultdict(list)
        self._queue: Deque[DomainEvent] = deque()
        self._is_dispatching = False
        self._last_processed_timestamp: float | None = None

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        if not isinstance(event_type, type) or not issubclass(event_type, DomainEvent):
            raise TypeError("event_type must be a DomainEvent subclass")

        if not callable(handler):
            raise TypeError("handler must be callable")

        subscribers = self._subscribers[event_type]
        if handler in subscribers:
            raise ValueError("duplicate subscriber for event type")

        subscribers.append(handler)

    def publish(self, event: DomainEvent) -> None:
        if not isinstance(event, DomainEvent):
            raise TypeError("event must be an instance of DomainEvent")

        self._queue.append(event)

        if self._is_dispatching:
            return

        self._is_dispatching = True
        try:
            while self._queue:
                current_event = self._queue.popleft()
                self._ensure_temporal_order(current_event)
                self._dispatch_event(current_event)
        finally:
            self._is_dispatching = False

    def _dispatch_event(self, event: DomainEvent) -> None:
        handlers = tuple(self._subscribers.get(type(event), ()))

        for handler in handlers:
            before = self._snapshot_event(event)
            handler(event)
            after = self._snapshot_event(event)

            if before != after:
                raise RuntimeError("event mutation detected during dispatch")

    def _ensure_temporal_order(self, event: DomainEvent) -> None:
        timestamp = event.timestamp
        if not isinstance(timestamp, Real):
            raise TypeError("event timestamp must be numeric")

        current_timestamp = float(timestamp)
        if self._last_processed_timestamp is not None and current_timestamp < self._last_processed_timestamp:
            raise ValueError("event processed out of temporal order")

        self._last_processed_timestamp = current_timestamp

    @staticmethod
    def _snapshot_event(event: DomainEvent) -> tuple[tuple[str, object], ...] | str:
        if is_dataclass(event):
            payload = asdict(event)
            return tuple(sorted(payload.items(), key=lambda item: item[0]))

        if hasattr(event, "__dict__"):
            payload = dict(getattr(event, "__dict__"))
            return tuple(sorted(payload.items(), key=lambda item: item[0]))

        return repr(event)
