
from decimal import Decimal

from aditi.data.importers.sbml import SBMLImportService
from aditi.modules.pathways import SBMLVisualizationWorkflow


def generate_chain_sbml(species_count: int) -> str:
    """Generate a valid SBML model containing a linear reaction chain."""

    if species_count < 2:
        raise ValueError("A pathway requires at least two species.")

    species = "\n".join(
        (
            f'<species id="s{i}" name="Metabolite {i}" '
            'compartment="cell" />'
        )
        for i in range(species_count)
    )

    reactions = "\n".join(
        (
            f'<reaction id="r{i}" name="Reaction {i}" '
            'reversible="false">'
            '<listOfReactants>'
            f'<speciesReference species="s{i}" stoichiometry="2"/>'
            '</listOfReactants>'
            '<listOfProducts>'
            f'<speciesReference species="s{i + 1}" '
            'stoichiometry="1"/>'
            '</listOfProducts>'
            '</reaction>'
        )
        for i in range(species_count - 1)
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <sbml xmlns="http://www.sbml.org/sbml/level3/version2/core"
          level="3" version="2">
        <model id="scale_test" name="Scale Test Pathway">
            <listOfCompartments>
                <compartment id="cell" constant="true"/>
            </listOfCompartments>
            <listOfSpecies>
                {species}
            </listOfSpecies>
            <listOfReactions>
                {reactions}
            </listOfReactions>
        </model>
    </sbml>
    """


def test_large_sbml_import_preserves_all_species_and_reactions() -> None:
    species_count = 500
    document = generate_chain_sbml(species_count)

    pathway = SBMLImportService().import_pathway(document)

    assert len(pathway.metabolites) == species_count
    assert len(pathway.reactions) == species_count - 1


def test_large_sbml_import_preserves_identifiers() -> None:
    species_count = 500
    pathway = SBMLImportService().import_pathway(
        generate_chain_sbml(species_count)
    )

    metabolite_ids = {
        identifier.value
        for metabolite in pathway.metabolites
        for identifier in metabolite.external_identifiers
        if identifier.namespace == "sbml"
    }

    reaction_ids = {
        identifier.value
        for reaction in pathway.reactions
        for identifier in reaction.external_identifiers
        if identifier.namespace == "sbml"
    }

    assert len(metabolite_ids) == species_count
    assert len(reaction_ids) == species_count - 1
    assert "s0" in metabolite_ids
    assert f"s{species_count - 1}" in metabolite_ids
    assert "r0" in reaction_ids
    assert f"r{species_count - 2}" in reaction_ids


def test_large_sbml_import_preserves_stoichiometry() -> None:
    species_count = 500
    pathway = SBMLImportService().import_pathway(
        generate_chain_sbml(species_count)
    )

    for reaction in pathway.reactions:
        assert len(reaction.reactants) == 1
        assert len(reaction.products) == 1
        assert reaction.reactants[0].coefficient == Decimal(2)
        assert reaction.products[0].coefficient == Decimal(1)


def test_large_sbml_import_preserves_shared_metabolite_identity() -> None:
    species_count = 500
    pathway = SBMLImportService().import_pathway(
        generate_chain_sbml(species_count)
    )

    for index in range(species_count - 2):
        current_product = pathway.reactions[index].products[0].metabolite
        next_reactant = pathway.reactions[index + 1].reactants[0].metabolite

        assert current_product is next_reactant


def test_large_sbml_visualization_generates_complete_scene() -> None:
    species_count = 100
    document = generate_chain_sbml(species_count)

    scene = SBMLVisualizationWorkflow().visualize(document)

    assert len(scene.metabolite_nodes) == species_count
    assert len(scene.reaction_nodes) == species_count - 1

    # Each reaction produces one reactant edge and one product edge.
    assert len(scene.edges) == 2 * (species_count - 1)

    assert len(scene.nodes) == 2 * species_count - 1


def test_large_sbml_visualization_assigns_all_node_positions() -> None:
    species_count = 100
    scene = SBMLVisualizationWorkflow().visualize(
        generate_chain_sbml(species_count)
    )

    assert all(node.position is not None for node in scene.nodes)

    position_identities = {
        node.position.identity
        for node in scene.nodes
    }

    assert len(position_identities) == len(scene.nodes)
