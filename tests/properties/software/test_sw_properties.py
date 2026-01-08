import pytest
from hypothesis import given, strategies as st
# test/domain/properties/test_sw_properties.py

"""

| Invariante | Cobertura                      |
| ---------- | ------------------------------ |
| SW1        | Integridade estrutural         |
| SW2        | Imutabilidade de contrato      |
| SW3        | Separação de responsabilidades |
| SW4        | Determinismo de interface      |


"""

valid_names = st.text(min_size=1).filter(lambda s: s.strip() != "")
invalid_names = st.one_of(st.none(), st.text(max_size=0))
valid_versions = st.from_regex(r"\d+\.\d+\.\d+", fullmatch=True)
invalid_versions = st.text().filter(lambda s: not bool(
    __import__("re").fullmatch(r"\d+\.\d+\.\d+", s)
))

@given(name=invalid_names, version=valid_versions)
def test_SW1_invalid_name_is_rejected(name, version):
    class Component:
        def name(self): return name
        def version(self): return version
        def dependencies(self): return []
        def invariants(self): return ["SW1"]
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    with pytest.raises(Exception):
        Component()
        
        
@given(name=valid_names, version=invalid_versions)
def test_SW1_invalid_version_is_rejected(name, version):
    class Component:
        def name(self): return name
        def version(self): return version
        def dependencies(self): return []
        def invariants(self): return ["SW1"]
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    with pytest.raises(Exception):
        Component()

def test_SW2_contract_metadata_is_immutable():
    class Component:
        def __init__(self):
            self._name = "comp"
            self._version = "1.0.0"

        def name(self): return self._name
        def version(self): return self._version
        def dependencies(self): return []
        def invariants(self): return ["SW2"]
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    c = Component()

    with pytest.raises(Exception):
        c._version = "2.0.0"  # mutação silenciosa proibida

@given(st.lists(st.sampled_from(["SW1", "SW2", "SW3", "SW4"]), min_size=1))
def test_SW3_component_cannot_claim_unimplemented_invariants(declared):
    class Component:
        def name(self): return "comp"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return declared
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

    if "SW3" in declared:
        with pytest.raises(Exception):
            Component()


@given(x=st.integers())
def test_SW4_interface_is_deterministic(x):
    class Component:
        def name(self): return "det"
        def version(self): return "1.0.0"
        def dependencies(self): return []
        def invariants(self): return ["SW4"]
        def validate_preconditions(self): pass
        def validate_postconditions(self): pass

        def compute(self, x):
            return x * 2

    c = Component()
    assert c.compute(x) == c.compute(x)

