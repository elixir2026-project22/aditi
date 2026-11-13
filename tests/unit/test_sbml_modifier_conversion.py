
from decimal import Decimal

from aditi.data.normalization.sbml import SBMLPathwayConverter
from aditi.data.parsers.sbml import (
    ParsedMetabolite,
    ParsedPathway,
    ParsedReaction,
    ParsedReactionParticipant,
)


def test_converter_deduplicates_repeated_modifier_species() -> None:
    parsed_pathway = ParsedPathway(
        identifier="modifier_test",
        name="Modifier Conversion Test",
        metabolites=(
            ParsedMetabolite(
                identifier="A",
                name="Alpha",
            ),
            ParsedMetabolite(
                identifier="B",
                name="Beta",
            ),
        ),
        reactions=(
            ParsedReaction(
                identifier="R1",
                name="Test Reaction",
                reactants=(
                    ParsedReactionParticipant(
                        metabolite_identifier="A",
                        coefficient=Decimal("1"),
                    ),
                ),
                products=(
                    ParsedReactionParticipant(
                        metabolite_identifier="B",
                        coefficient=Decimal("1"),
                    ),
                ),
                reversible=False,
                modifiers=(
                    ParsedReactionParticipant(
                        metabolite_identifier="A",
                        coefficient=Decimal("1"),
                        metaid="modifier_one",
                    ),
                    ParsedReactionParticipant(
                        metabolite_identifier="A",
                        coefficient=Decimal("1"),
                        metaid="modifier_two",
                    ),
                    ParsedReactionParticipant(
                        metabolite_identifier="A",
                        coefficient=Decimal("1"),
                        metaid="modifier_three",
                    ),
                ),
            ),
        ),
    )

    pathway = SBMLPathwayConverter().convert(parsed_pathway)

    assert len(pathway.reactions) == 1

    reaction = pathway.reactions[0]

    assert len(reaction.reactants) == 1
    assert len(reaction.products) == 1
    assert len(reaction.modifiers) == 1

    assert (
        reaction.modifiers[0].metabolite
        is reaction.reactants[0].metabolite
    )

    assert reaction.modifiers[0].metabolite.name == "Alpha"
    assert reaction.modifiers[0].coefficient == Decimal("1")


def test_converter_preserves_distinct_modifier_species() -> None:
    parsed_pathway = ParsedPathway(
        identifier="distinct_modifiers",
        name="Distinct Modifier Test",
        metabolites=(
            ParsedMetabolite(identifier="A", name="Alpha"),
            ParsedMetabolite(identifier="B", name="Beta"),
            ParsedMetabolite(identifier="C", name="Gamma"),
        ),
        reactions=(
            ParsedReaction(
                identifier="R1",
                name="Test Reaction",
                reactants=(
                    ParsedReactionParticipant("A"),
                ),
                products=(
                    ParsedReactionParticipant("B"),
                ),
                reversible=False,
                modifiers=(
                    ParsedReactionParticipant(
                        "A",
                        metaid="modifier_one",
                    ),
                    ParsedReactionParticipant(
                        "C",
                        metaid="modifier_two",
                    ),
                    ParsedReactionParticipant(
                        "C",
                        metaid="modifier_three",
                    ),
                ),
            ),
        ),
    )

    pathway = SBMLPathwayConverter().convert(parsed_pathway)

    reaction = pathway.reactions[0]

    assert len(reaction.modifiers) == 2

    assert [
        participant.metabolite.name
        for participant in reaction.modifiers
    ] == ["Alpha", "Gamma"]
