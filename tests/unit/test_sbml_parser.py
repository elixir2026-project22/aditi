
from decimal import Decimal

import pytest

from aditi.data.parsers.sbml import (
    SBMLParseError,
    SBMLParser,
)


def sample_sbml() -> str:
    """Return a minimal SBML Level 3 document."""

    return """<?xml version="1.0" encoding="UTF-8"?>
    <sbml xmlns="http://www.sbml.org/sbml/level3/version2/core"
          level="3" version="2">
        <model id="glycolysis" name="Glycolysis">
            <listOfCompartments>
                <compartment id="cell" constant="true"/>
            </listOfCompartments>
            <listOfSpecies>
                <species id="glucose"
                         name="Glucose"
                         compartment="cell"
                         hasOnlySubstanceUnits="false"
                         boundaryCondition="false"
                         constant="false"/>
                <species id="g6p"
                         name="Glucose 6-phosphate"
                         compartment="cell"
                         hasOnlySubstanceUnits="false"
                         boundaryCondition="false"
                         constant="false"/>
            </listOfSpecies>
            <listOfReactions>
                <reaction id="hexokinase"
                          name="Hexokinase"
                          reversible="false">
                    <listOfReactants>
                        <speciesReference species="glucose"
                                           stoichiometry="1"/>
                    </listOfReactants>
                    <listOfProducts>
                        <speciesReference species="g6p"
                                           stoichiometry="1"/>
                    </listOfProducts>
                </reaction>
            </listOfReactions>
        </model>
    </sbml>
    """


@pytest.fixture
def parser() -> SBMLParser:
    return SBMLParser()


def test_parser_reads_pathway_metadata(parser):
    result = parser.parse(sample_sbml())

    assert result.identifier == "glycolysis"
    assert result.name == "Glycolysis"


def test_parser_reads_species_as_metabolites(parser):
    result = parser.parse(sample_sbml())

    assert len(result.metabolites) == 2

    glucose = result.metabolites[0]

    assert glucose.identifier == "glucose"
    assert glucose.name == "Glucose"
    assert glucose.chemical_formula is None
    assert glucose.charge is None


def test_parser_reads_reaction_metadata(parser):
    result = parser.parse(sample_sbml())

    assert len(result.reactions) == 1

    reaction = result.reactions[0]

    assert reaction.identifier == "hexokinase"
    assert reaction.name == "Hexokinase"
    assert reaction.reversible is False


def test_parser_reads_reaction_participants(parser):
    result = parser.parse(sample_sbml())

    reaction = result.reactions[0]

    assert reaction.reactants[0].metabolite_identifier == "glucose"
    assert reaction.products[0].metabolite_identifier == "g6p"


def test_parser_reads_stoichiometric_coefficients(parser):
    document = sample_sbml().replace(
        'stoichiometry="1"',
        'stoichiometry="2"',
        1,
    )

    result = parser.parse(document)

    assert (
        result.reactions[0].reactants[0].coefficient
        == Decimal(2)
    )

def test_parser_defaults_missing_stoichiometry_to_one(parser):
    document = sample_sbml().replace(
        ' stoichiometry="1"',
        "",
    )

    result = parser.parse(document)

    assert result.reactions[0].reactants[0].coefficient == Decimal(1)


def test_parser_defaults_missing_reversible_attribute_to_true(parser):
    document = sample_sbml().replace(
        'reversible="false"',
        "",
    )

    result = parser.parse(document)

    assert result.reactions[0].reversible is True


def test_parser_supports_bytes_input(parser):
    result = parser.parse(sample_sbml().encode("utf-8"))

    assert result.name == "Glycolysis"


def test_parser_rejects_empty_document(parser):
    with pytest.raises(SBMLParseError, match="cannot be empty"):
        parser.parse("")


def test_parser_rejects_malformed_xml(parser):
    with pytest.raises(SBMLParseError, match="Invalid SBML XML"):
        parser.parse("<sbml><model>")


def test_parser_rejects_non_sbml_root(parser):
    with pytest.raises(SBMLParseError, match="root must be an SBML"):
        parser.parse("<document/>")


def test_parser_rejects_missing_model(parser):
    document = """<sbml xmlns="http://www.sbml.org/sbml/level3/version2/core"/>"""

    with pytest.raises(SBMLParseError, match="does not contain a model"):
        parser.parse(document)


def test_parser_rejects_unknown_species_reference(parser):
    document = sample_sbml().replace(
        'species="glucose"',
        'species="unknown"',
        1,
    )

    with pytest.raises(SBMLParseError, match="unknown species"):
        parser.parse(document)


def test_parser_rejects_duplicate_species_ids(parser):
    document = sample_sbml().replace(
        '<species id="g6p"',
        '<species id="glucose"',
    )

    with pytest.raises(SBMLParseError, match="Duplicate SBML species"):
        parser.parse(document)


def test_parser_rejects_duplicate_reaction_ids(parser):
    document = sample_sbml().replace(
        "</listOfReactions>",
        """
        <reaction id="hexokinase">
            <listOfReactants>
                <speciesReference species="glucose"/>
            </listOfReactants>
            <listOfProducts>
                <speciesReference species="g6p"/>
            </listOfProducts>
        </reaction>
        </listOfReactions>
        """,
    )

    with pytest.raises(SBMLParseError, match="Duplicate SBML reaction"):
        parser.parse(document)

@pytest.mark.parametrize(
    "coefficient",
    ["0", "-1", "NaN", "Infinity", "-Infinity", "invalid"],
)
def test_parser_rejects_invalid_stoichiometry(parser, coefficient):
    document = sample_sbml().replace(
        'stoichiometry="1"',
        f'stoichiometry="{coefficient}"',
        1,
    )

    with pytest.raises(SBMLParseError):
        parser.parse(document)


def test_parser_rejects_invalid_reversible_value(parser):
    document = sample_sbml().replace(
        'reversible="false"',
        'reversible="sometimes"',
    )

    with pytest.raises(SBMLParseError, match="invalid reversible"):
        parser.parse(document)


def test_parser_rejects_reaction_without_products(parser):
    document = sample_sbml().replace(
        '<listOfProducts>',
        '<listOfProducts>',
    )

    document = document.replace(
        '<speciesReference species="g6p"',
        '<!-- removed product --> <speciesReference species="g6p"',
    )

    document = document.replace(
        '<!-- removed product --> <speciesReference species="g6p"',
        '<!-- removed product -->',
    )

    with pytest.raises(SBMLParseError, match="at least one reactant"):
        parser.parse(document)


def test_parser_supports_modifier_species_references(parser):
    document = sample_sbml().replace(
        "</reaction>",
        """
        <listOfModifiers>
            <modifierSpeciesReference species="glucose"/>
        </listOfModifiers>
        </reaction>
        """,
    )

    result = parser.parse(document)

    assert len(result.reactions) == 1

    reaction = result.reactions[0]

    assert len(reaction.modifiers) == 1
    assert reaction.modifiers[0].metabolite_identifier == "glucose"
    assert reaction.modifiers[0].coefficient == Decimal("1")

def test_parser_rejects_doctype_declarations(parser):
    document = """<!DOCTYPE sbml [
        <!ENTITY test "unsafe">
    ]>""" + sample_sbml()

    with pytest.raises(SBMLParseError, match="DOCTYPE and ENTITY"):
        parser.parse(document)


def test_parser_rejects_non_string_input(parser):
    with pytest.raises(TypeError, match="string or bytes"):
        parser.parse(123)


def test_parser_preserves_repeated_modifier_references(parser):
    document = sample_sbml().replace(
        "</reaction>",
        """
        <listOfModifiers>
            <modifierSpeciesReference
                species="glucose"
                metaid="modifier_one"/>
            <modifierSpeciesReference
                species="glucose"
                metaid="modifier_two"/>
            <modifierSpeciesReference
                species="glucose"
                metaid="modifier_three"/>
        </listOfModifiers>
        </reaction>
        """,
    )

    result = parser.parse(document)

    modifiers = result.reactions[0].modifiers

    assert len(modifiers) == 3

    assert all(
        modifier.metabolite_identifier == "glucose"
        for modifier in modifiers
    )

    assert [modifier.metaid for modifier in modifiers] == [
        "modifier_one",
        "modifier_two",
        "modifier_three",
    ]