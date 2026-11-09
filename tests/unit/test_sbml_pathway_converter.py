
from decimal import Decimal

import pytest

from aditi.data.normalization.sbml import (
    SBMLConversionError,
    SBMLPathwayConverter,
)
from aditi.data.parsers.sbml import (
    ParsedMetabolite,
    ParsedPathway,
    ParsedReaction,
    ParsedReactionParticipant,
)
from aditi.domain.pathways.pathway import Pathway


@pytest.fixture
def converter() -> SBMLPathwayConverter:
    return SBMLPathwayConverter()


@pytest.fixture
def parsed_pathway() -> ParsedPathway:
    return ParsedPathway(
        identifier="glycolysis",
        name="Glycolysis",
        metabolites=(
            ParsedMetabolite(
                identifier="glucose",
                name="Glucose",
                chemical_formula="C6H12O6",
                charge=0,
            ),
            ParsedMetabolite(
                identifier="g6p",
                name="Glucose 6-phosphate",
                chemical_formula="C6H13O9P",
                charge=-2,
            ),
            ParsedMetabolite(
                identifier="f6p",
                name="Fructose 6-phosphate",
                chemical_formula="C6H13O9P",
                charge=-2,
            ),
        ),
        reactions=(
            ParsedReaction(
                identifier="hexokinase",
                name="Hexokinase",
                reactants=(
                    ParsedReactionParticipant(
                        metabolite_identifier="glucose",
                        coefficient=Decimal(1),
                    ),
                ),
                products=(
                    ParsedReactionParticipant(
                        metabolite_identifier="g6p",
                        coefficient=Decimal(1),
                    ),
                ),
                reversible=False,
            ),
            ParsedReaction(
                identifier="phosphoglucose_isomerase",
                name="Phosphoglucose isomerase",
                reactants=(
                    ParsedReactionParticipant(
                        metabolite_identifier="g6p",
                        coefficient=Decimal(1),
                    ),
                ),
                products=(
                    ParsedReactionParticipant(
                        metabolite_identifier="f6p",
                        coefficient=Decimal(1),
                    ),
                ),
                reversible=True,
            ),
        ),
    )


def test_converter_returns_domain_pathway(converter, parsed_pathway):
    result = converter.convert(parsed_pathway)

    assert isinstance(result, Pathway)
    assert result.name == "Glycolysis"
    assert len(result.reactions) == 2


def test_converter_preserves_metabolite_properties(
    converter,
    parsed_pathway,
):
    result = converter.convert(parsed_pathway)

    glucose = result.metabolites[0]

    assert glucose.name == "Glucose"
    assert glucose.chemical_formula == "C6H12O6"
    assert glucose.charge == 0


def test_converter_preserves_reaction_properties(
    converter,
    parsed_pathway,
):
    result = converter.convert(parsed_pathway)

    assert result.reactions[0].name == "Hexokinase"
    assert result.reactions[0].reversible is False

    assert result.reactions[1].name == "Phosphoglucose isomerase"
    assert result.reactions[1].reversible is True


def test_converter_preserves_stoichiometric_coefficients(
    converter,
    parsed_pathway,
):
    result = converter.convert(parsed_pathway)

    participant = result.reactions[0].reactants[0]

    assert participant.coefficient == Decimal(1)


def test_converter_preserves_shared_metabolite_identity(
    converter,
    parsed_pathway,
):
    result = converter.convert(parsed_pathway)

    first_reaction_product = result.reactions[0].products[0].metabolite
    second_reaction_reactant = result.reactions[1].reactants[0].metabolite

    assert first_reaction_product is second_reaction_reactant
    assert first_reaction_product.identity == second_reaction_reactant.identity


def test_converter_preserves_sbml_external_identifiers(
    converter,
    parsed_pathway,
):
    result = converter.convert(parsed_pathway)

    assert result.external_identifiers[0].namespace == "sbml"
    assert result.external_identifiers[0].value == "glycolysis"

    glucose = result.metabolites[0]

    assert glucose.external_identifiers[0].namespace == "sbml"
    assert glucose.external_identifiers[0].value == "glucose"

    reaction = result.reactions[0]

    assert reaction.external_identifiers[0].namespace == "sbml"
    assert reaction.external_identifiers[0].value == "hexokinase"


def test_converter_generates_independent_internal_identities(
    converter,
    parsed_pathway,
):
    first = converter.convert(parsed_pathway)
    second = converter.convert(parsed_pathway)

    assert first.identity != second.identity
    assert (
        first.metabolites[0].identity
        != second.metabolites[0].identity
    )


def test_converter_preserves_reaction_participant_order(
    converter,
    parsed_pathway,
):
    result = converter.convert(parsed_pathway)

    assert result.reactions[0].reactants[0].metabolite.name == "Glucose"
    assert (
        result.reactions[0].products[0].metabolite.name
        == "Glucose 6-phosphate"
    )


def test_converter_rejects_non_parsed_pathway(converter):
    with pytest.raises(TypeError, match="ParsedPathway"):
        converter.convert("not a pathway")


def test_converter_rejects_duplicate_metabolite_identifiers(
    converter,
    parsed_pathway,
):
    duplicate = ParsedMetabolite(
        identifier="glucose",
        name="Duplicate glucose",
    )

    invalid_pathway = ParsedPathway(
        identifier=parsed_pathway.identifier,
        name=parsed_pathway.name,
        metabolites=parsed_pathway.metabolites + (duplicate,),
        reactions=parsed_pathway.reactions,
    )

    with pytest.raises(
        SBMLConversionError,
        match="Duplicate SBML metabolite",
    ):
        converter.convert(invalid_pathway)


def test_converter_rejects_duplicate_reaction_identifiers(
    converter,
    parsed_pathway,
):
    duplicate = parsed_pathway.reactions[0]

    invalid_pathway = ParsedPathway(
        identifier=parsed_pathway.identifier,
        name=parsed_pathway.name,
        metabolites=parsed_pathway.metabolites,
        reactions=parsed_pathway.reactions + (duplicate,),
    )

    with pytest.raises(
        SBMLConversionError,
        match="Duplicate SBML reaction",
    ):
        converter.convert(invalid_pathway)


def test_converter_rejects_unknown_metabolite_references(
    converter,
    parsed_pathway,
):
    reaction = ParsedReaction(
        identifier="invalid_reaction",
        name="Invalid reaction",
        reactants=(
            ParsedReactionParticipant(
                metabolite_identifier="unknown",
            ),
        ),
        products=(
            ParsedReactionParticipant(
                metabolite_identifier="glucose",
            ),
        ),
        reversible=False,
    )

    invalid_pathway = ParsedPathway(
        identifier=parsed_pathway.identifier,
        name=parsed_pathway.name,
        metabolites=parsed_pathway.metabolites,
        reactions=(reaction,),
    )

    with pytest.raises(
        SBMLConversionError,
        match="unknown metabolite",
    ):
        converter.convert(invalid_pathway)


def test_converter_rejects_pathway_without_reactions(converter):
    invalid_pathway = ParsedPathway(
        identifier="empty",
        name="Empty pathway",
        metabolites=(
            ParsedMetabolite(
                identifier="glucose",
                name="Glucose",
            ),
        ),
        reactions=(),
    )

    with pytest.raises(
        SBMLConversionError,
        match="Could not construct domain pathway",
    ):
        converter.convert(invalid_pathway)
