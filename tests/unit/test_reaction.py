
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways.metabolite import Metabolite
from aditi.domain.pathways.reaction import (
    Reaction,
    ReactionParticipant,
)


@pytest.fixture
def glucose():
    return Metabolite(name="Glucose")


@pytest.fixture
def atp():
    return Metabolite(name="ATP")


@pytest.fixture
def glucose_6_phosphate():
    return Metabolite(name="Glucose-6-phosphate")


@pytest.fixture
def adp():
    return Metabolite(name="ADP")


@pytest.fixture
def reaction_participants(
    glucose,
    atp,
    glucose_6_phosphate,
    adp,
):
    reactants = (
        ReactionParticipant(glucose, Decimal(1)),
        ReactionParticipant(atp, Decimal(1)),
    )

    products = (
        ReactionParticipant(
            glucose_6_phosphate,
            Decimal(1),
        ),
        ReactionParticipant(adp, Decimal(1)),
    )

    return reactants, products


def test_create_reaction(reaction_participants):
    reactants, products = reaction_participants

    reaction = Reaction(
        name="Glucose phosphorylation",
        reactants=reactants,
        products=products,
    )

    assert reaction.name == "Glucose phosphorylation"
    assert reaction.reactants == reactants
    assert reaction.products == products
    assert reaction.reversible is False
    assert reaction.entity_type == "reaction"


def test_create_reversible_reaction(reaction_participants):
    reactants, products = reaction_participants

    reaction = Reaction(
        name="Glucose phosphorylation",
        reactants=reactants,
        products=products,
        reversible=True,
    )

    assert reaction.reversible is True


def test_reaction_inherits_internal_identity():
    reaction = Reaction(
        name="Example reaction",
        reactants=(
            ReactionParticipant(
                Metabolite(name="A"),
            ),
        ),
        products=(
            ReactionParticipant(
                Metabolite(name="B"),
            ),
        ),
    )

    assert isinstance(reaction.identity, EntityIdentity)


def test_reaction_accepts_existing_identity():
    identity = EntityIdentity.generate()

    reaction = Reaction(
        name="Example reaction",
        identity=identity,
        reactants=(
            ReactionParticipant(Metabolite(name="A")),
        ),
        products=(
            ReactionParticipant(Metabolite(name="B")),
        ),
    )

    assert reaction.identity == identity


def test_reaction_participant_default_coefficient(glucose):
    participant = ReactionParticipant(glucose)

    assert participant.coefficient == Decimal(1)


def test_reaction_participant_accepts_fractional_coefficient(glucose):
    participant = ReactionParticipant(
        glucose,
        Decimal("0.5"),
    )

    assert participant.coefficient == Decimal("0.5")


@pytest.mark.parametrize(
    "coefficient",
    [
        Decimal(0),
        Decimal(-1),
        Decimal("-0.5"),
    ],
)
def test_reject_non_positive_coefficients(glucose, coefficient):
    with pytest.raises(ValueError, match="greater than zero"):
        ReactionParticipant(
            glucose,
            coefficient,
        )


@pytest.mark.parametrize(
    "coefficient",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_reject_non_finite_coefficients(glucose, coefficient):
    with pytest.raises(ValueError, match="finite"):
        ReactionParticipant(
            glucose,
            coefficient,
        )


@pytest.mark.parametrize(
    "coefficient",
    [
        1,
        0.5,
        "1",
        True,
    ],
)
def test_reject_non_decimal_coefficients(glucose, coefficient):
    with pytest.raises(TypeError, match="Decimal"):
        ReactionParticipant(
            glucose,
            coefficient,
        )


def test_reject_non_metabolite_participant():
    with pytest.raises(TypeError, match="Metabolite"):
        ReactionParticipant(
            metabolite="Glucose",
        )


def test_reject_empty_reaction_name():
    with pytest.raises(ValueError, match="name"):
        Reaction(
            name="",
            reactants=(ReactionParticipant(Metabolite(name="A")),),
            products=(ReactionParticipant(Metabolite(name="B")),),
        )


def test_reject_reaction_name_with_whitespace():
    with pytest.raises(ValueError, match="leading or trailing"):
        Reaction(
            name=" Example reaction ",
            reactants=(ReactionParticipant(Metabolite(name="A")),),
            products=(ReactionParticipant(Metabolite(name="B")),),
        )


def test_reject_empty_reactants():
    with pytest.raises(ValueError, match="at least one reactant"):
        Reaction(
            name="Example reaction",
            reactants=(),
            products=(ReactionParticipant(Metabolite(name="B")),),
        )


def test_reject_empty_products():
    with pytest.raises(ValueError, match="at least one product"):
        Reaction(
            name="Example reaction",
            reactants=(ReactionParticipant(Metabolite(name="A")),),
            products=(),
        )


def test_reject_non_tuple_reactants():
    with pytest.raises(TypeError, match="reactants"):
        Reaction(
            name="Example reaction",
            reactants=[ReactionParticipant(Metabolite(name="A"))],
            products=(ReactionParticipant(Metabolite(name="B")),),
        )


def test_reject_non_tuple_products():
    with pytest.raises(TypeError, match="products"):
        Reaction(
            name="Example reaction",
            reactants=(ReactionParticipant(Metabolite(name="A")),),
            products=[ReactionParticipant(Metabolite(name="B"))],
        )


def test_reject_invalid_reactant_participant():
    with pytest.raises(TypeError, match="ReactionParticipant"):
        Reaction(
            name="Example reaction",
            reactants=("Glucose",),
            products=(ReactionParticipant(Metabolite(name="B")),),
        )


def test_reject_invalid_product_participant():
    with pytest.raises(TypeError, match="ReactionParticipant"):
        Reaction(
            name="Example reaction",
            reactants=(ReactionParticipant(Metabolite(name="A")),),
            products=("Product",),
        )


def test_reject_duplicate_reactants(glucose):
    with pytest.raises(ValueError, match="duplicate metabolites"):
        Reaction(
            name="Example reaction",
            reactants=(
                ReactionParticipant(glucose),
                ReactionParticipant(glucose),
            ),
            products=(ReactionParticipant(Metabolite(name="B")),),
        )


def test_reject_duplicate_products(glucose):
    with pytest.raises(ValueError, match="duplicate metabolites"):
        Reaction(
            name="Example reaction",
            reactants=(ReactionParticipant(Metabolite(name="A")),),
            products=(
                ReactionParticipant(glucose),
                ReactionParticipant(glucose),
            ),
        )


def test_allow_same_metabolite_on_both_sides(glucose):
    reaction = Reaction(
        name="Example reaction",
        reactants=(ReactionParticipant(glucose),),
        products=(ReactionParticipant(glucose),),
    )

    assert reaction.reactants[0].metabolite == reaction.products[0].metabolite


@pytest.mark.parametrize(
    "reversible",
    [
        "yes",
        1,
        0,
        None,
    ],
)
def test_reject_invalid_reversibility(reversible):
    with pytest.raises(TypeError, match="boolean"):
        Reaction(
            name="Example reaction",
            reactants=(ReactionParticipant(Metabolite(name="A")),),
            products=(ReactionParticipant(Metabolite(name="B")),),
            reversible=reversible,
        )


def test_reaction_participant_is_immutable(glucose):
    participant = ReactionParticipant(glucose)

    with pytest.raises(FrozenInstanceError):
        participant.coefficient = Decimal(2)


def test_reaction_is_immutable():
    reaction = Reaction(
        name="Example reaction",
        reactants=(ReactionParticipant(Metabolite(name="A")),),
        products=(ReactionParticipant(Metabolite(name="B")),),
    )

    with pytest.raises(FrozenInstanceError):
        reaction.name = "Changed reaction"


def test_reaction_is_hashable():
    reaction = Reaction(
        name="Example reaction",
        reactants=(ReactionParticipant(Metabolite(name="A")),),
        products=(ReactionParticipant(Metabolite(name="B")),),
    )

    assert isinstance(hash(reaction), int)
