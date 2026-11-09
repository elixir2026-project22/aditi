
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from aditi.domain.entities.identifiers import ExternalIdentifier
from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways import (
    Metabolite,
    Pathway,
    Reaction,
    ReactionParticipant,
)


@pytest.fixture
def glucose():
    return Metabolite(
        name="Glucose",
        chemical_formula="C6H12O6",
    )


@pytest.fixture
def glucose_6_phosphate():
    return Metabolite(
        name="Glucose-6-phosphate",
    )


@pytest.fixture
def fructose_6_phosphate():
    return Metabolite(
        name="Fructose-6-phosphate",
    )


@pytest.fixture
def first_reaction(glucose, glucose_6_phosphate):
    return Reaction(
        name="Glucose phosphorylation",
        reactants=(
            ReactionParticipant(glucose, Decimal(1)),
        ),
        products=(
            ReactionParticipant(
                glucose_6_phosphate,
                Decimal(1),
            ),
        ),
    )


@pytest.fixture
def second_reaction(
    glucose_6_phosphate,
    fructose_6_phosphate,
):
    return Reaction(
        name="Glucose-6-phosphate isomerization",
        reactants=(
            ReactionParticipant(
                glucose_6_phosphate,
                Decimal(1),
            ),
        ),
        products=(
            ReactionParticipant(
                fructose_6_phosphate,
                Decimal(1),
            ),
        ),
    )


@pytest.fixture
def pathway(first_reaction, second_reaction):
    return Pathway(
        name="Example metabolic pathway",
        description="A pathway containing two reactions.",
        reactions=(
            first_reaction,
            second_reaction,
        ),
    )


def test_create_pathway(pathway):
    assert pathway.name == "Example metabolic pathway"
    assert pathway.description == "A pathway containing two reactions."
    assert len(pathway.reactions) == 2
    assert pathway.entity_type == "pathway"


def test_create_pathway_without_description(first_reaction):
    pathway = Pathway(
        name="Example pathway",
        reactions=(first_reaction,),
    )

    assert pathway.description is None


def test_pathway_inherits_internal_identity(pathway):
    assert isinstance(pathway.identity, EntityIdentity)


def test_pathway_accepts_existing_identity(first_reaction):
    identity = EntityIdentity.generate()

    pathway = Pathway(
        name="Example pathway",
        identity=identity,
        reactions=(first_reaction,),
    )

    assert pathway.identity == identity


def test_pathway_accepts_external_identifiers(first_reaction):
    identifier = ExternalIdentifier(
        namespace="Reactome",
        value="R-HSA-70171",
    )

    pathway = Pathway(
        name="Example pathway",
        external_identifiers=(identifier,),
        reactions=(first_reaction,),
    )

    assert pathway.external_identifiers == (identifier,)


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        " Example pathway",
        "Example pathway ",
        None,
        123,
    ],
)
def test_reject_invalid_pathway_name(first_reaction, name):
    with pytest.raises(ValueError, match="name"):
        Pathway(
            name=name,
            reactions=(first_reaction,),
        )


@pytest.mark.parametrize(
    "description",
    [
        "",
        " ",
        " Example description",
        "Example description ",
        123,
    ],
)
def test_reject_invalid_description(first_reaction, description):
    with pytest.raises(ValueError, match="description"):
        Pathway(
            name="Example pathway",
            description=description,
            reactions=(first_reaction,),
        )


def test_reject_empty_reactions():
    with pytest.raises(ValueError, match="at least one reaction"):
        Pathway(
            name="Example pathway",
            reactions=(),
        )


def test_reject_non_tuple_reactions(first_reaction):
    with pytest.raises(TypeError, match="tuple"):
        Pathway(
            name="Example pathway",
            reactions=[first_reaction],
        )


def test_reject_invalid_reaction():
    with pytest.raises(TypeError, match="Reaction instances"):
        Pathway(
            name="Example pathway",
            reactions=("Invalid reaction",),
        )


def test_reject_duplicate_reactions(first_reaction):
    with pytest.raises(ValueError, match="duplicate reactions"):
        Pathway(
            name="Example pathway",
            reactions=(
                first_reaction,
                first_reaction,
            ),
        )


def test_preserve_reaction_order(pathway, first_reaction, second_reaction):
    assert pathway.reactions == (
        first_reaction,
        second_reaction,
    )


def test_derive_pathway_metabolites(pathway, glucose_6_phosphate):
    metabolites = pathway.metabolites

    assert [metabolite.name for metabolite in metabolites] == [
        "Glucose",
        "Glucose-6-phosphate",
        "Fructose-6-phosphate",
    ]


def test_derived_metabolites_are_unique(pathway):
    metabolites = pathway.metabolites
    identities = [metabolite.identity for metabolite in metabolites]

    assert len(identities) == len(set(identities))


def test_metabolites_are_ordered_by_first_appearance(pathway):
    assert pathway.metabolites[0].name == "Glucose"
    assert pathway.metabolites[1].name == "Glucose-6-phosphate"


def test_pathway_metabolites_include_reactants_and_products(
    first_reaction,
    glucose,
    glucose_6_phosphate,
):
    pathway = Pathway(
        name="Example pathway",
        reactions=(first_reaction,),
    )

    assert pathway.metabolites == (
        glucose,
        glucose_6_phosphate,
    )


def test_pathway_is_immutable(pathway):
    with pytest.raises(FrozenInstanceError):
        pathway.name = "Changed pathway"


def test_pathway_is_hashable(pathway):
    assert isinstance(hash(pathway), int)


def test_pathways_have_unique_internal_identities(
    first_reaction,
    second_reaction,
):
    first = Pathway(
        name="First pathway",
        reactions=(first_reaction,),
    )

    second = Pathway(
        name="Second pathway",
        reactions=(second_reaction,),
    )

    assert first.identity != second.identity
