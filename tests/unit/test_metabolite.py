
from dataclasses import FrozenInstanceError

import pytest

from aditi.domain.entities.identifiers import ExternalIdentifier
from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways.metabolite import Metabolite


def test_create_metabolite():
    metabolite = Metabolite(name="Glucose")

    assert metabolite.name == "Glucose"
    assert metabolite.chemical_formula is None
    assert metabolite.charge is None
    assert metabolite.entity_type == "metabolite"


def test_create_metabolite_with_chemical_properties():
    metabolite = Metabolite(
        name="Glucose",
        chemical_formula="C6H12O6",
        charge=0,
    )

    assert metabolite.chemical_formula == "C6H12O6"
    assert metabolite.charge == 0


def test_metabolite_inherits_internal_identity():
    metabolite = Metabolite(name="Glucose")

    assert isinstance(metabolite.identity, EntityIdentity)


def test_metabolite_accepts_existing_identity():
    identity = EntityIdentity.generate()

    metabolite = Metabolite(
        name="Glucose",
        identity=identity,
    )

    assert metabolite.identity == identity


def test_metabolite_accepts_external_identifiers():
    identifier = ExternalIdentifier(
        namespace="ChEBI",
        value="CHEBI:17234",
    )

    metabolite = Metabolite(
        name="Glucose",
        external_identifiers=(identifier,),
    )

    assert metabolite.external_identifiers == (identifier,)


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        " Glucose",
        "Glucose ",
        None,
        123,
    ],
)
def test_reject_invalid_metabolite_name(name):
    with pytest.raises(ValueError, match="name"):
        Metabolite(name=name)


@pytest.mark.parametrize(
    "formula",
    [
        "",
        " ",
        " C6H12O6",
        "C6H12O6 ",
        123,
    ],
)
def test_reject_invalid_chemical_formula(formula):
    with pytest.raises(ValueError, match="Chemical formula"):
        Metabolite(
            name="Glucose",
            chemical_formula=formula,
        )


def test_accept_missing_chemical_formula():
    metabolite = Metabolite(name="Unknown metabolite")

    assert metabolite.chemical_formula is None


@pytest.mark.parametrize(
    "charge",
    [
        1.5,
        "1",
        True,
        False,
    ],
)
def test_reject_invalid_charge(charge):
    with pytest.raises(TypeError, match="integer"):
        Metabolite(
            name="Glucose",
            charge=charge,
        )


@pytest.mark.parametrize(
    "charge",
    [
        -2,
        -1,
        0,
        1,
        2,
    ],
)
def test_accept_integer_charge(charge):
    metabolite = Metabolite(
        name="Example metabolite",
        charge=charge,
    )

    assert metabolite.charge == charge


def test_metabolite_is_immutable():
    metabolite = Metabolite(name="Glucose")

    with pytest.raises(FrozenInstanceError):
        metabolite.name = "Fructose"


def test_metabolites_have_unique_internal_identities():
    first = Metabolite(name="Glucose")
    second = Metabolite(name="Fructose")

    assert first.identity != second.identity


def test_metabolite_is_hashable():
    first = Metabolite(name="Glucose")
    second = Metabolite(name="Fructose")

    metabolites = {first, second}

    assert len(metabolites) == 2


def test_metabolite_equality():
    identity = EntityIdentity.generate()

    first = Metabolite(
        name="Glucose",
        identity=identity,
    )

    second = Metabolite(
        name="Glucose",
        identity=identity,
    )

    assert first == second
