
from decimal import Decimal

import pytest
from pydantic import ValidationError

from aditi.api import (
    PathwayDefinitionRequest,
    PathwayGraphBuilder,
)
from aditi.domain.pathways import (
    GraphEdgeRole,
    GraphNodeType,
)


def create_definition() -> PathwayDefinitionRequest:
    return PathwayDefinitionRequest(
        name="Glycolysis",
        description="A simplified glycolysis pathway.",
        metabolites=(
            {
                "id": "glucose",
                "name": "Glucose",
                "chemical_formula": "C6H12O6",
            },
            {
                "id": "g6p",
                "name": "Glucose-6-phosphate",
                "chemical_formula": "C6H13O9P",
                "charge": -2,
            },
            {
                "id": "f6p",
                "name": "Fructose-6-phosphate",
                "chemical_formula": "C6H13O9P",
                "charge": -2,
            },
        ),
        reactions=(
            {
                "id": "r1",
                "name": "Glucose phosphorylation",
                "reactants": (
                    {
                        "metabolite_id": "glucose",
                        "coefficient": "1",
                    },
                ),
                "products": (
                    {
                        "metabolite_id": "g6p",
                        "coefficient": "1",
                    },
                ),
            },
            {
                "id": "r2",
                "name": "Phosphoglucose isomerization",
                "reactants": (
                    {
                        "metabolite_id": "g6p",
                        "coefficient": "1",
                    },
                ),
                "products": (
                    {
                        "metabolite_id": "f6p",
                        "coefficient": "1",
                    },
                ),
                "reversible": True,
            },
        ),
    )


def test_builder_creates_pathway_graph() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    assert graph.pathway_identity is not None
    assert len(graph.metabolite_nodes) == 3
    assert len(graph.reaction_nodes) == 2


def test_builder_preserves_pathway_metabolite_names() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    assert {
        node.entity.name
        for node in graph.metabolite_nodes
    } == {
        "Glucose",
        "Glucose-6-phosphate",
        "Fructose-6-phosphate",
    }


def test_builder_preserves_metabolite_formula_and_charge() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    metabolites = {
        node.entity.name: node.entity
        for node in graph.metabolite_nodes
    }

    glucose = metabolites["Glucose"]
    g6p = metabolites["Glucose-6-phosphate"]

    assert glucose.chemical_formula == "C6H12O6"
    assert glucose.charge is None

    assert g6p.chemical_formula == "C6H13O9P"
    assert g6p.charge == -2


def test_builder_preserves_reaction_names() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    assert {
        node.entity.name
        for node in graph.reaction_nodes
    } == {
        "Glucose phosphorylation",
        "Phosphoglucose isomerization",
    }


def test_builder_preserves_reaction_reversibility() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    reactions = {
        node.entity.name: node.entity
        for node in graph.reaction_nodes
    }

    assert reactions["Glucose phosphorylation"].reversible is False
    assert reactions["Phosphoglucose isomerization"].reversible is True


def test_builder_preserves_edge_coefficients() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    assert all(
        edge.coefficient == Decimal(1)
        for edge in graph.edges
    )


def test_builder_preserves_edge_roles() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    assert {
        edge.role
        for edge in graph.edges
    } == {
        GraphEdgeRole.REACTANT,
        GraphEdgeRole.PRODUCT,
    }


def test_builder_preserves_graph_node_types() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    assert all(
        node.node_type == GraphNodeType.METABOLITE
        for node in graph.metabolite_nodes
    )

    assert all(
        node.node_type == GraphNodeType.REACTION
        for node in graph.reaction_nodes
    )


def test_builder_creates_unique_internal_identities() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    identities = [
        node.identity
        for node in graph.nodes
    ]

    assert len(identities) == len(set(identities))


def test_builder_reuses_metabolite_identity_across_reactions() -> None:
    graph = PathwayGraphBuilder().build(
        create_definition()
    )

    g6p_node = next(
        node
        for node in graph.metabolite_nodes
        if node.entity.name == "Glucose-6-phosphate"
    )

    connected_edges = [
        edge
        for edge in graph.edges
        if (
            edge.source_identity == g6p_node.identity
            or edge.target_identity == g6p_node.identity
        )
    ]

    assert len(connected_edges) == 2


def test_builder_generates_independent_pathway_identities() -> None:
    builder = PathwayGraphBuilder()
    definition = create_definition()

    first = builder.build(definition)
    second = builder.build(definition)

    assert first.pathway_identity != second.pathway_identity


def test_builder_rejects_invalid_definition() -> None:
    with pytest.raises(TypeError):
        PathwayGraphBuilder().build("invalid")


def test_request_rejects_duplicate_metabolite_ids() -> None:
    definition = create_definition().model_dump()

    definition["metabolites"] = (
        definition["metabolites"][0],
        definition["metabolites"][0],
    )

    with pytest.raises(ValidationError):
        PathwayDefinitionRequest(**definition)


def test_request_rejects_duplicate_reaction_ids() -> None:
    definition = create_definition().model_dump()

    definition["reactions"] = (
        definition["reactions"][0],
        definition["reactions"][0],
    )

    with pytest.raises(ValidationError):
        PathwayDefinitionRequest(**definition)


def test_request_rejects_unknown_metabolite_reference() -> None:
    definition = create_definition().model_dump()

    definition["reactions"][0]["reactants"] = (
        {
            "metabolite_id": "unknown",
            "coefficient": Decimal(1),
        },
    )

    with pytest.raises(ValidationError):
        PathwayDefinitionRequest(**definition)


def test_request_rejects_duplicate_reactants() -> None:
    definition = create_definition().model_dump()

    definition["reactions"][0]["reactants"] = (
        {
            "metabolite_id": "glucose",
            "coefficient": Decimal(1),
        },
        {
            "metabolite_id": "glucose",
            "coefficient": Decimal(2),
        },
    )

    with pytest.raises(ValidationError):
        PathwayDefinitionRequest(**definition)


def test_request_rejects_duplicate_products() -> None:
    definition = create_definition().model_dump()

    definition["reactions"][0]["products"] = (
        {
            "metabolite_id": "g6p",
            "coefficient": Decimal(1),
        },
        {
            "metabolite_id": "g6p",
            "coefficient": Decimal(2),
        },
    )

    with pytest.raises(ValidationError):
        PathwayDefinitionRequest(**definition)


def test_request_rejects_empty_reaction_participants() -> None:
    definition = create_definition().model_dump()

    definition["reactions"][0]["reactants"] = ()

    with pytest.raises(ValidationError):
        PathwayDefinitionRequest(**definition)


def test_request_rejects_non_positive_coefficient() -> None:
    definition = create_definition().model_dump()

    definition["reactions"][0]["reactants"] = (
        {
            "metabolite_id": "glucose",
            "coefficient": Decimal(0),
        },
    )

    with pytest.raises(ValidationError):
        PathwayDefinitionRequest(**definition)


def test_request_rejects_empty_pathway() -> None:
    with pytest.raises(ValidationError):
        PathwayDefinitionRequest(
            name="Empty pathway",
            metabolites=(),
            reactions=(),
        )
