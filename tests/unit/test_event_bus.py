from __future__ import annotations

from dataclasses import dataclass

import pytest

from domain.event_bus import InternalEventBus
from domain.events import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class SampleEvent(DomainEvent):
    label: str

    def _event_marker(self) -> None:
        return None


def test_t1_order_is_preserved_in_dispatch():
    bus = InternalEventBus()
    received: list[str] = []

    def handler(event: DomainEvent) -> None:
        received.append(event.label)

    bus.subscribe(SampleEvent, handler)

    bus.publish(SampleEvent(label="A", timestamp=1.0))
    bus.publish(SampleEvent(label="B", timestamp=2.0))

    assert received == ["A", "B"]


def test_t2_each_subscriber_receives_event_exactly_once():
    bus = InternalEventBus()
    calls = {"h1": 0, "h2": 0}

    def handler_one(event: DomainEvent) -> None:
        calls["h1"] += 1

    def handler_two(event: DomainEvent) -> None:
        calls["h2"] += 1

    bus.subscribe(SampleEvent, handler_one)
    bus.subscribe(SampleEvent, handler_two)

    bus.publish(SampleEvent(label="single", timestamp=1.0))

    assert calls == {"h1": 1, "h2": 1}


def test_t3_causal_chaining_is_processed_before_publish_returns():
    bus = InternalEventBus()
    received: list[str] = []

    def chain_handler(event: DomainEvent) -> None:
        received.append(event.label)
        if event.label == "E1":
            bus.publish(SampleEvent(label="E2", timestamp=2.0))

    bus.subscribe(SampleEvent, chain_handler)

    bus.publish(SampleEvent(label="E1", timestamp=1.0))

    assert received == ["E1", "E2"]


def test_t4_dispatch_is_deterministic_for_same_inputs():
    def run_once() -> list[str]:
        bus = InternalEventBus()
        history: list[str] = []

        def recorder(event: DomainEvent) -> None:
            history.append(f"{event.label}@{event.timestamp}")

        bus.subscribe(SampleEvent, recorder)
        bus.publish(SampleEvent(label="A", timestamp=1.0))
        bus.publish(SampleEvent(label="B", timestamp=2.0))
        return history

    first = run_once()
    second = run_once()

    assert first == second


def test_t5_long_chain_does_not_require_recursion():
    bus = InternalEventBus()
    max_depth = 2000
    processed = 0

    def handler(event: DomainEvent) -> None:
        nonlocal processed
        processed += 1
        value = int(event.label)
        if value < max_depth:
            bus.publish(SampleEvent(label=str(value + 1), timestamp=float(value + 1)))

    bus.subscribe(SampleEvent, handler)
    bus.publish(SampleEvent(label="1", timestamp=1.0))

    assert processed == max_depth


def test_duplicate_subscriber_is_rejected():
    bus = InternalEventBus()

    def handler(event: DomainEvent) -> None:
        return None

    bus.subscribe(SampleEvent, handler)

    with pytest.raises(ValueError, match="duplicate subscriber"):
        bus.subscribe(SampleEvent, handler)


def test_out_of_order_temporal_processing_is_rejected():
    bus = InternalEventBus()
    bus.publish(SampleEvent(label="first", timestamp=2.0))

    with pytest.raises(ValueError, match="out of temporal order"):
        bus.publish(SampleEvent(label="second", timestamp=1.0))


def test_event_mutation_is_detected_during_dispatch():
    bus = InternalEventBus()

    def mutating_handler(event: DomainEvent) -> None:
        object.__setattr__(event, "label", "mutated")

    bus.subscribe(SampleEvent, mutating_handler)

    with pytest.raises(RuntimeError, match="mutation detected"):
        bus.publish(SampleEvent(label="safe", timestamp=1.0))
