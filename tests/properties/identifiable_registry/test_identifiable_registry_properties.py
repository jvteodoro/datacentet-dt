import pytest

from domain.core.identifiable import Identifiable
from domain.core.identifiable_registry import (
    IdentifiableRegistry,
    IdentifiableRegistryViolation,
)


def make_param(name, value, ts):
    return Identifiable(
        name=name,
        estimated_value=value,
        uncertainty=0.1,
        timestamp=ts,
        method="test",
        support=["y"],
    )


def test_IR1_only_identifiables_can_be_registered():
    reg = IdentifiableRegistry()

    with pytest.raises(IdentifiableRegistryViolation):
        reg.register("not_identifiable")  # type: ignore


def test_IR2_only_one_active_per_name():
    reg = IdentifiableRegistry()

    p1 = make_param("gain", 2.0, 1)
    p2 = make_param("gain", 3.0, 2)

    reg.register(p1)
    reg.register(p2)

    current = reg.get_current("gain")

    assert current.estimated_value == 3.0


def test_IR3_older_parameter_cannot_override_newer():
    reg = IdentifiableRegistry()

    p_new = make_param("gain", 3.0, 5)
    p_old = make_param("gain", 2.0, 3)

    reg.register(p_new)
    reg.register(p_old)

    current = reg.get_current("gain")

    assert current.timestamp == 5


def test_get_all_current_returns_only_latest_versions():
    reg = IdentifiableRegistry()

    reg.register(make_param("gain", 2.0, 1))
    reg.register(make_param("offset", 1.0, 2))
    reg.register(make_param("gain", 3.0, 3))

    params = reg.get_all_current()

    names = {p.name for p in params}
    assert names == {"gain", "offset"}


def test_latest_timestamp():
    reg = IdentifiableRegistry()

    assert reg.latest_timestamp() is None

    reg.register(make_param("gain", 2.0, 4))
    reg.register(make_param("offset", 1.0, 6))

    assert reg.latest_timestamp() == 6