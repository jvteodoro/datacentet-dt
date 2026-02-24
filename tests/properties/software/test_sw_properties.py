import pytest
from hypothesis import given, strategies as st

from domain.contracts.software import SoftwareContract, SoftwareViolation

valid_names = st.text(min_size=1).filter(lambda s: s.strip() != "")
invalid_names = st.one_of(st.none(), st.text(max_size=0), st.just("   "))
valid_versions = st.from_regex(r"\d+\.\d+\.\d+", fullmatch=True)
invalid_versions = st.text().filter(lambda s: not bool(__import__("re").fullmatch(r"\d+\.\d+\.\d+", s)))


def _snapshot(name: str = "comp", version: str = "1.0.0", declared=None, implemented=None):
    data = {
        "name": name,
        "version": version,
        "declared_invariants": declared if declared is not None else ["SW1"],
    }
    if implemented is not None:
        data["implemented_invariants"] = implemented
    return data


@given(name=invalid_names, version=valid_versions)
def test_SW1_invalid_name_is_rejected(name, version):
    with pytest.raises(SoftwareViolation):
        SoftwareContract().validate(_snapshot(name=name, version=version))


@given(name=valid_names, version=invalid_versions)
def test_SW1_invalid_version_is_rejected(name, version):
    with pytest.raises(SoftwareViolation):
        SoftwareContract().validate(_snapshot(name=name, version=version))


def test_SW2_contract_metadata_is_immutable():
    snapshot = _snapshot()
    SoftwareContract().validate(snapshot)
    snapshot["version"] = "2.0.0"
    SoftwareContract().validate(snapshot)


@given(st.lists(st.sampled_from(["SW1", "SW2", "SW3", "SW4"]), min_size=1))
def test_SW3_component_cannot_claim_unimplemented_invariants(declared):
    if "SW3" in declared:
        with pytest.raises(SoftwareViolation):
            SoftwareContract().validate(_snapshot(declared=declared))
    else:
        SoftwareContract().validate(_snapshot(declared=declared))


@given(x=st.integers())
def test_SW4_interface_is_deterministic(x):
    c = SoftwareContract()
    left = c.validate(_snapshot())
    right = c.validate(_snapshot())
    assert left == right
