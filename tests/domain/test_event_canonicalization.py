from uuid import UUID

import pytest

from digital_twin.domain.event import DomainEvent, normalize_event


def test_event_id_is_deterministic_when_not_provided() -> None:
    event_a = DomainEvent(timestamp=10, type="tick", payload={"a": 1}, version=1)
    event_b = DomainEvent(timestamp=10, type="tick", payload={"a": 1}, version=1)

    assert isinstance(event_a.event_id, UUID)
    assert event_a.event_id == event_b.event_id


def test_payload_is_immutable_mapping() -> None:
    source_payload = {"a": 1}
    event = DomainEvent(timestamp=1, type="tick", payload=source_payload)

    source_payload["a"] = 2
    assert event.payload["a"] == 1

    with pytest.raises(TypeError):
        event.payload["a"] = 99


def test_normalize_event_trims_type_without_changing_event_id() -> None:
    event = DomainEvent(timestamp=1, type=" tick ", payload={"x": 1}, version=1)

    normalized = normalize_event(event)

    assert normalized.type == "tick"
    assert normalized.event_id == event.event_id
