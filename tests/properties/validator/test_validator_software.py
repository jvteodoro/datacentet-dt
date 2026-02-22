import pytest
import numpy as np

from domain.contracts.software import SoftwareContract, SoftwareViolation
from domain.core.snapshot import Snapshot, SoftwareMetadataViolation
from domain.core.observable import Observable
from domain.core.state_variable import StateVariable
from domain.core.state_vector import StateVector
from domain.core.identifiable import Identifiable


def build_inputs():
    obs = [
        Observable(
            name="voltage",
            value=230.0,
            uncertainty=1.0,
            timestamp=0,
            source="sensor",
        )
    ]

    sv = StateVector(
        variables=[
            StateVariable(
                name="v",
                value=230.0,
                uncertainty=1.0,
                timestamp=0,
            )
        ],
        covariance=np.array([[1.0]]),
    )

    param = Identifiable(
        name="resistance",
        estimated_value=0.5,
        uncertainty=0.1,
        timestamp=0,
        method="least_squares",
        support=["voltage"],
    )
    return obs, sv, [param]


def valid_snapshot():
    obs, sv, identifiables = build_inputs()
    return Snapshot(
        observables=obs,
        state_vector=sv,
        identifiables=identifiables,
        component_id="comp-1",
        component_type="energy",
        name="EnergySubsystem",
        version="1.0.0",
        declared_invariants=["SW1", "SW2"],
        dependencies=[],
    )


def test_SW_invalid_version_is_rejected():
    obs, sv, identifiables = build_inputs()

    with pytest.raises(SoftwareMetadataViolation):
        Snapshot(
            observables=obs,
            state_vector=sv,
            identifiables=identifiables,
            component_id="comp-1",
            component_type="energy",
            name="EnergySubsystem",
            version="1",  # inválido
            declared_invariants=["SW1"],
            dependencies=[],
        )


def test_SW_snapshot_enforces_name_and_version_contract():
    obs, sv, identifiables = build_inputs()

    with pytest.raises(SoftwareMetadataViolation):
        Snapshot(
            observables=obs,
            state_vector=sv,
            identifiables=identifiables,
            component_id="comp-1",
            component_type="energy",
            name="   ",
            version="1.0.0",
            declared_invariants=["SW1"],
            dependencies=[],
        )

    with pytest.raises(SoftwareMetadataViolation):
        Snapshot(
            observables=obs,
            state_vector=sv,
            identifiables=identifiables,
            component_id="comp-1",
            component_type="energy",
            name="EnergySubsystem",
            version="one",
            declared_invariants=["SW1"],
            dependencies=[],
        )


def test_SW_snapshot_views_are_defensively_copied():
    snap = valid_snapshot()

    sw = snap.to_software_view()
    sw["declared_invariants"].append("SW4")
    assert snap.to_software_view()["declared_invariants"] == ["SW1", "SW2"]

    obs = snap.observables
    obs[0]["value"] = -1
    assert snap.observables[0]["value"] == 230.0


def test_SW_declared_invariants_must_be_supported_subset():
    sw_view = valid_snapshot().to_software_view()
    sw_view["declared_invariants"] = ["SW9"]

    with pytest.raises(SoftwareViolation):
        SoftwareContract().validate(sw_view)
