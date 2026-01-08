import pytest

from domain.core.observable import Observable
from domain.core.observable_registry import (
    ObservableRegistry,
    ObservableRegistryViolation,
)


def test_OR1_only_observables_can_be_registered():
    reg = ObservableRegistry()

    with pytest.raises(ObservableRegistryViolation):
        reg.register("not_an_observable")  # type: ignore


def test_OR3_observables_are_returned_in_temporal_order():
    reg = ObservableRegistry()

    o1 = Observable(
        name="y",
        value=1.0,
        uncertainty=0.1,
        timestamp=2,
        source="sensor",
    )
    o2 = Observable(
        name="y",
        value=2.0,
        uncertainty=0.1,
        timestamp=1,
        source="sensor",
    )

    reg.register(o1)
    reg.register(o2)

    obs = reg.get_since(0)

    assert [o.timestamp for o in obs] == [1, 2]


def test_OR2_registry_never_returns_future_data():
    reg = ObservableRegistry()

    o = Observable(
        name="y",
        value=5.0,
        uncertainty=0.2,
        timestamp=10,
        source="sensor",
    )

    reg.register(o)

    obs = reg.get_at(timestamp=5)

    assert obs == []


def test_get_at_returns_only_matching_timestamp():
    reg = ObservableRegistry()

    o1 = Observable(
        name="y",
        value=1.0,
        uncertainty=0.1,
        timestamp=1,
        source="sensor",
    )
    o2 = Observable(
        name="y",
        value=2.0,
        uncertainty=0.1,
        timestamp=2,
        source="sensor",
    )

    reg.register(o1)
    reg.register(o2)

    obs = reg.get_at(2)

    assert obs == [o2]


def test_latest_timestamp():
    reg = ObservableRegistry()

    assert reg.latest_timestamp() is None

    reg.register(
        Observable(
            name="y",
            value=1.0,
            uncertainty=0.1,
            timestamp=3,
            source="sensor",
        )
    )

    assert reg.latest_timestamp() == 3