
import pytest

from aditi.data.importers.sbml import SBMLImportService
from aditi.data.normalization.sbml import (
    SBMLPathwayConverter,
)
from aditi.data.parsers.sbml import (
    SBMLParseError,
    SBMLParser,
)
from aditi.domain.pathways.pathway import Pathway


def sample_sbml() -> str:
    """Return a minimal SBML Level 3 document."""

    return """<?xml version="1.0" encoding="UTF-8"?>
    <sbml xmlns="http://www.sbml.org/sbml/level3/version2/core"
          level="3" version="2">
        <model id="glycolysis" name="Glycolysis">
            <listOfSpecies>
                <species id="glucose"
                         name="Glucose"
                         compartment="cell"/>
                <species id="g6p"
                         name="Glucose 6-phosphate"
                         compartment="cell"/>
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
                                           stoichiometry="2"/>
                    </listOfProducts>
                </reaction>
            </listOfReactions>
        </model>
    </sbml>
    """


@pytest.fixture
def service() -> SBMLImportService:
    return SBMLImportService()


def test_import_service_returns_domain_pathway(service):
    result = service.import_pathway(sample_sbml())

    assert isinstance(result, Pathway)
    assert result.name == "Glycolysis"


def test_import_service_preserves_metabolites(service):
    result = service.import_pathway(sample_sbml())

    assert len(result.metabolites) == 2

    names = {
        metabolite.name
        for metabolite in result.metabolites
    }

    assert names == {
        "Glucose",
        "Glucose 6-phosphate",
    }


def test_import_service_preserves_reactions(service):
    result = service.import_pathway(sample_sbml())

    assert len(result.reactions) == 1

    reaction = result.reactions[0]

    assert reaction.name == "Hexokinase"
    assert reaction.reversible is False


def test_import_service_preserves_stoichiometry(service):
    result = service.import_pathway(sample_sbml())

    reaction = result.reactions[0]

    assert reaction.reactants[0].coefficient == 1
    assert reaction.products[0].coefficient == 2


def test_import_service_preserves_sbml_identifiers(service):
    result = service.import_pathway(sample_sbml())

    assert result.external_identifiers[0].namespace == "sbml"
    assert result.external_identifiers[0].value == "glycolysis"


def test_import_service_accepts_bytes(service):
    result = service.import_pathway(
        sample_sbml().encode("utf-8")
    )

    assert result.name == "Glycolysis"


def test_import_service_propagates_parser_errors(service):
    with pytest.raises(SBMLParseError):
        service.import_pathway("<invalid")


def test_import_service_rejects_invalid_source_type(service):
    with pytest.raises(TypeError, match="string or bytes"):
        service.import_pathway(123)


def test_import_service_accepts_injected_components():
    parser = SBMLParser()
    converter = SBMLPathwayConverter()

    service = SBMLImportService(
        parser=parser,
        converter=converter,
    )

    result = service.import_pathway(sample_sbml())

    assert isinstance(result, Pathway)


def test_import_service_rejects_invalid_parser():
    with pytest.raises(TypeError, match="SBMLParser"):
        SBMLImportService(parser=object())


def test_import_service_rejects_invalid_converter():
    with pytest.raises(TypeError, match="SBMLPathwayConverter"):
        SBMLImportService(converter=object())


def test_import_service_creates_independent_domain_identities(service):
    first = service.import_pathway(sample_sbml())
    second = service.import_pathway(sample_sbml())

    assert first.identity != second.identity
    assert (
        first.metabolites[0].identity
        != second.metabolites[0].identity
    )


def test_import_service_preserves_shared_metabolite_identity(service):
    result = service.import_pathway(sample_sbml())

    reaction = result.reactions[0]

    # The same imported metabolite object is used wherever
    # its SBML identifier is referenced.
    assert reaction.reactants[0].metabolite is result.metabolites[0]
