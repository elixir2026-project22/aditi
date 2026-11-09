
from decimal import Decimal

import pytest

from aditi.data.importers.sbml import SBMLImportService
from aditi.data.parsers.sbml import SBMLParseError
from aditi.domain.pathways.graph import GraphEdgeRole
from aditi.modules.pathways import SBMLVisualizationWorkflow
from aditi.visualization.pathways.layouts.registry import LayoutRegistryError
from aditi.visualization.pathways.scene import PathwayScene
from aditi.visualization.pathways.service import PathwayVisualizationService


def sample_sbml() -> str:
    """Return a small SBML pathway with two reactions."""

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
                <species id="f6p"
                         name="Fructose 6-phosphate"
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
                <reaction id="isomerase"
                          name="Phosphoglucose isomerase"
                          reversible="true">
                    <listOfReactants>
                        <speciesReference species="g6p"
                                           stoichiometry="1"/>
                    </listOfReactants>
                    <listOfProducts>
                        <speciesReference species="f6p"
                                           stoichiometry="1"/>
                    </listOfProducts>
                </reaction>
            </listOfReactions>
        </model>
    </sbml>
    """


@pytest.fixture
def workflow() -> SBMLVisualizationWorkflow:
    return SBMLVisualizationWorkflow()


def test_workflow_returns_pathway_scene(workflow):
    result = workflow.visualize(sample_sbml())

    assert isinstance(result, PathwayScene)


def test_workflow_preserves_pathway_identity(workflow):
    result = workflow.visualize(sample_sbml())

    assert result.pathway_identity is not None


def test_workflow_generates_all_metabolite_nodes(workflow):
    result = workflow.visualize(sample_sbml())

    assert len(result.metabolite_nodes) == 3

    labels = {
        node.label
        for node in result.metabolite_nodes
    }

    assert labels == {
        "Glucose",
        "Glucose 6-phosphate",
        "Fructose 6-phosphate",
    }


def test_workflow_generates_all_reaction_nodes(workflow):
    result = workflow.visualize(sample_sbml())

    assert len(result.reaction_nodes) == 2

    labels = {
        node.label
        for node in result.reaction_nodes
    }

    assert labels == {
        "Hexokinase",
        "Phosphoglucose isomerase",
    }


def test_workflow_generates_correct_edge_count(workflow):
    result = workflow.visualize(sample_sbml())

    # Two reactant edges and two product edges.
    assert len(result.edges) == 4


def test_workflow_preserves_edge_coefficients(workflow):
    result = workflow.visualize(sample_sbml())

    coefficients = {
        edge.coefficient
        for edge in result.edges
    }

    assert Decimal(1) in coefficients
    assert Decimal(2) in coefficients


def test_workflow_preserves_edge_directions(workflow):
    result = workflow.visualize(sample_sbml())

    metabolite_ids = {
        node.identity
        for node in result.metabolite_nodes
    }

    reaction_ids = {
        node.identity
        for node in result.reaction_nodes
    }

    for edge in result.edges:
        if edge.role is GraphEdgeRole.REACTANT:
            assert edge.source_identity in metabolite_ids
            assert edge.target_identity in reaction_ids

        elif edge.role is GraphEdgeRole.PRODUCT:
            assert edge.source_identity in reaction_ids
            assert edge.target_identity in metabolite_ids

def test_workflow_generates_node_positions(workflow):
    result = workflow.visualize(sample_sbml())

    assert all(
        node.position is not None
        for node in result.nodes
    )

    assert len({
        node.position.identity
        for node in result.nodes
    }) == len(result.nodes)


def test_workflow_supports_force_directed_layout(workflow):
    result = workflow.visualize(
        sample_sbml(),
        layout_id="force-directed",
    )

    assert isinstance(result, PathwayScene)
    assert len(result.nodes) == 5


def test_workflow_exposes_available_layouts(workflow):
    assert "hierarchical" in workflow.available_layouts
    assert "force-directed" in workflow.available_layouts


def test_workflow_rejects_unknown_layout(workflow):
    with pytest.raises(LayoutRegistryError):
        workflow.visualize(
            sample_sbml(),
            layout_id="unknown-layout",
        )


def test_workflow_propagates_sbml_parse_errors(workflow):
    with pytest.raises(SBMLParseError):
        workflow.visualize("<invalid")


def test_workflow_rejects_invalid_source_type(workflow):
    with pytest.raises(TypeError, match="string or bytes"):
        workflow.visualize(123)


def test_workflow_rejects_empty_layout_identifier(workflow):
    with pytest.raises(ValueError, match="non-empty"):
        workflow.visualize(
            sample_sbml(),
            layout_id=" ",
        )


def test_workflow_accepts_injected_services():
    workflow = SBMLVisualizationWorkflow(
        import_service=SBMLImportService(),
        visualization_service=PathwayVisualizationService(),
    )

    result = workflow.visualize(sample_sbml())

    assert isinstance(result, PathwayScene)


def test_workflow_rejects_invalid_import_service():
    with pytest.raises(TypeError, match="SBMLImportService"):
        SBMLVisualizationWorkflow(import_service=object())


def test_workflow_rejects_invalid_visualization_service():
    with pytest.raises(
        TypeError,
        match="PathwayVisualizationService",
    ):
        SBMLVisualizationWorkflow(
            visualization_service=object(),
        )


def test_workflow_creates_independent_scenes_for_repeated_imports(
    workflow,
):
    first = workflow.visualize(sample_sbml())
    second = workflow.visualize(sample_sbml())

    assert first.pathway_identity != second.pathway_identity
