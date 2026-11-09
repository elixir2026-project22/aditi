
from decimal import Decimal

import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways import (
    GraphEdge,
    GraphEdgeRole,
    GraphNode,
    GraphNodeType,
    Metabolite,
    Pathway,
    PathwayGraph,
    Reaction,
    ReactionParticipant,
)


@pytest.fixture
def glucose():
    return Metabolite(name="Glucose")


@pytest.fixture
def glucose_6_phosphate():
    return Metabolite(name="Glucose-6-phosphate")


@pytest.fixture
def fructose_6_phosphate():
    return Metabolite(name="Fructose-6-phosphate")


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
        name="Example pathway",
        reactions=(
            first_reaction,
            second_reaction,
        ),
    )


@pytest.fixture
def pathway_graph(pathway):
    return PathwayGraph.from_pathway(pathway)


def test_create_metabolite_graph_node(glucose):
    node = GraphNode(glucose)

    assert node.identity == glucose.identity
    assert node.node_type is GraphNodeType.METABOLITE


def test_create_reaction_graph_node(first_reaction):
    node = GraphNode(first_reaction)

    assert node.identity == first_reaction.identity
    assert node.node_type is GraphNodeType.REACTION


def test_reject_invalid_graph_node():
    with pytest.raises(TypeError, match="Metabolite or Reaction"):
        GraphNode("Glucose")


def test_create_reactant_graph_edge(glucose, first_reaction):
    edge = GraphEdge(
        source_identity=glucose.identity,
        target_identity=first_reaction.identity,
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(1),
    )

    assert edge.role is GraphEdgeRole.REACTANT
    assert edge.coefficient == Decimal(1)


def test_create_product_graph_edge(first_reaction, glucose_6_phosphate):
    edge = GraphEdge(
        source_identity=first_reaction.identity,
        target_identity=glucose_6_phosphate.identity,
        role=GraphEdgeRole.PRODUCT,
        coefficient=Decimal(1),
    )

    assert edge.role is GraphEdgeRole.PRODUCT


def test_reject_invalid_edge_identities():
    with pytest.raises(TypeError, match="source"):
        GraphEdge(
            source_identity="invalid",
            target_identity=EntityIdentity.generate(),
            role=GraphEdgeRole.REACTANT,
            coefficient=Decimal(1),
        )


def test_reject_invalid_edge_role(glucose, first_reaction):
    with pytest.raises(TypeError, match="GraphEdgeRole"):
        GraphEdge(
            source_identity=glucose.identity,
            target_identity=first_reaction.identity,
            role="reactant",
            coefficient=Decimal(1),
        )


@pytest.mark.parametrize(
    "coefficient",
    [
        Decimal(0),
        Decimal(-1),
    ],
)
def test_reject_non_positive_edge_coefficient(
    glucose,
    first_reaction,
    coefficient,
):
    with pytest.raises(ValueError, match="greater than zero"):
        GraphEdge(
            source_identity=glucose.identity,
            target_identity=first_reaction.identity,
            role=GraphEdgeRole.REACTANT,
            coefficient=coefficient,
        )


def test_reject_non_finite_edge_coefficient(glucose, first_reaction):
    with pytest.raises(ValueError, match="finite"):
        GraphEdge(
            source_identity=glucose.identity,
            target_identity=first_reaction.identity,
            role=GraphEdgeRole.REACTANT,
            coefficient=Decimal("Infinity"),
        )


def test_reject_non_decimal_edge_coefficient(glucose, first_reaction):
    with pytest.raises(TypeError, match="Decimal"):
        GraphEdge(
            source_identity=glucose.identity,
            target_identity=first_reaction.identity,
            role=GraphEdgeRole.REACTANT,
            coefficient=1,
        )


def test_build_graph_from_pathway(pathway_graph):
    assert isinstance(pathway_graph, PathwayGraph)


def test_graph_preserves_pathway_identity(pathway, pathway_graph):
    assert pathway_graph.pathway_identity == pathway.identity


def test_graph_contains_unique_metabolite_nodes(pathway_graph):
    assert len(pathway_graph.metabolite_nodes) == 3


def test_graph_contains_reaction_nodes(pathway_graph):
    assert len(pathway_graph.reaction_nodes) == 2


def test_graph_contains_expected_node_count(pathway_graph):
    assert len(pathway_graph.nodes) == 5


def test_graph_contains_expected_edge_count(pathway_graph):
    assert len(pathway_graph.edges) == 4


def test_graph_preserves_reactant_edge_direction(
    pathway_graph,
    glucose,
    first_reaction,
):
    edge = pathway_graph.edges[0]

    assert edge.source_identity == glucose.identity
    assert edge.target_identity == first_reaction.identity
    assert edge.role is GraphEdgeRole.REACTANT


def test_graph_preserves_product_edge_direction(
    pathway_graph,
    first_reaction,
    glucose_6_phosphate,
):
    edge = pathway_graph.edges[1]

    assert edge.source_identity == first_reaction.identity
    assert edge.target_identity == glucose_6_phosphate.identity
    assert edge.role is GraphEdgeRole.PRODUCT


def test_graph_preserves_stoichiometric_coefficients(
    glucose,
    glucose_6_phosphate,
):
    reaction = Reaction(
        name="Example reaction",
        reactants=(
            ReactionParticipant(glucose, Decimal(2)),
        ),
        products=(
            ReactionParticipant(
                glucose_6_phosphate,
                Decimal("0.5"),
            ),
        ),
    )

    pathway = Pathway(
        name="Example pathway",
        reactions=(reaction,),
    )

    graph = PathwayGraph.from_pathway(pathway)

    assert graph.edges[0].coefficient == Decimal(2)
    assert graph.edges[1].coefficient == Decimal("0.5")


def test_graph_nodes_reference_original_entities(
    pathway_graph,
    glucose,
):
    glucose_node = next(
        node
        for node in pathway_graph.metabolite_nodes
        if node.identity == glucose.identity
    )

    assert glucose_node.entity is glucose


def test_graph_preserves_reaction_reversibility():
    reactant = Metabolite(name="A")
    product = Metabolite(name="B")

    reaction = Reaction(
        name="Reversible reaction",
        reactants=(ReactionParticipant(reactant),),
        products=(ReactionParticipant(product),),
        reversible=True,
    )

    pathway = Pathway(
        name="Example pathway",
        reactions=(reaction,),
    )

    graph = PathwayGraph.from_pathway(pathway)

    reaction_node = graph.reaction_nodes[0]

    assert reaction_node.entity.reversible is True


def test_reject_invalid_pathway_for_graph_construction():
    with pytest.raises(TypeError, match="Pathway instance"):
        PathwayGraph.from_pathway("not a pathway")


def test_reject_invalid_pathway_graph_identity(pathway_graph):
    with pytest.raises(TypeError, match="EntityIdentity"):
        PathwayGraph(
            pathway_identity="invalid",
            nodes=pathway_graph.nodes,
            edges=pathway_graph.edges,
        )


def test_reject_non_tuple_graph_nodes(pathway_graph):
    with pytest.raises(TypeError, match="nodes"):
        PathwayGraph(
            pathway_identity=pathway_graph.pathway_identity,
            nodes=list(pathway_graph.nodes),
            edges=pathway_graph.edges,
        )


def test_reject_duplicate_graph_nodes(glucose, pathway):
    node = GraphNode(glucose)

    with pytest.raises(ValueError, match="duplicate nodes"):
        PathwayGraph(
            pathway_identity=pathway.identity,
            nodes=(node, node),
            edges=(),
        )


def test_reject_edges_with_missing_nodes(glucose, pathway):
    edge = GraphEdge(
        source_identity=glucose.identity,
        target_identity=EntityIdentity.generate(),
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(1),
    )

    with pytest.raises(ValueError, match="does not exist"):
        PathwayGraph(
            pathway_identity=pathway.identity,
            nodes=(GraphNode(glucose),),
            edges=(edge,),
        )


def test_reject_invalid_reactant_edge_direction(
    glucose,
    first_reaction,
    pathway,
):
    edge = GraphEdge(
        source_identity=first_reaction.identity,
        target_identity=glucose.identity,
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(1),
    )

    with pytest.raises(ValueError, match="Invalid direction"):
        PathwayGraph(
            pathway_identity=pathway.identity,
            nodes=(
                GraphNode(glucose),
                GraphNode(first_reaction),
            ),
            edges=(edge,),
        )


def test_reject_invalid_product_edge_direction(
    glucose,
    first_reaction,
    pathway,
):
    edge = GraphEdge(
        source_identity=glucose.identity,
        target_identity=first_reaction.identity,
        role=GraphEdgeRole.PRODUCT,
        coefficient=Decimal(1),
    )

    with pytest.raises(ValueError, match="Invalid direction"):
        PathwayGraph(
            pathway_identity=pathway.identity,
            nodes=(
                GraphNode(glucose),
                GraphNode(first_reaction),
            ),
            edges=(edge,),
        )


def test_reject_duplicate_graph_edges(glucose, first_reaction, pathway):
    edge = GraphEdge(
        source_identity=glucose.identity,
        target_identity=first_reaction.identity,
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(1),
    )

    with pytest.raises(ValueError, match="duplicate edges"):
        PathwayGraph(
            pathway_identity=pathway.identity,
            nodes=(
                GraphNode(glucose),
                GraphNode(first_reaction),
            ),
            edges=(edge, edge),
        )
