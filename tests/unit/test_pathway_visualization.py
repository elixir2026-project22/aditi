
from decimal import Decimal

import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways import (
    GraphEdgeRole,
    GraphNodeType,
    Metabolite,
    Pathway,
    PathwayGraph,
    Reaction,
    ReactionParticipant,
)
from aditi.visualization.pathways import (
    PathwayVisualEdge,
    PathwayVisualization,
    PathwayVisualNode,
)


@pytest.fixture
def glucose():
    return Metabolite(name="Glucose")


@pytest.fixture
def glucose_6_phosphate():
    return Metabolite(name="Glucose-6-phosphate")


@pytest.fixture
def reaction(glucose, glucose_6_phosphate):
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
def pathway(reaction):
    return Pathway(
        name="Example pathway",
        reactions=(reaction,),
    )


@pytest.fixture
def pathway_graph(pathway):
    return PathwayGraph.from_pathway(pathway)


@pytest.fixture
def visualization(pathway_graph):
    return PathwayVisualization.from_graph(pathway_graph)


def test_create_visual_node():
    identity = EntityIdentity.generate()

    node = PathwayVisualNode(
        identity=identity,
        node_type=GraphNodeType.METABOLITE,
        label="Glucose",
    )

    assert node.identity == identity
    assert node.node_type is GraphNodeType.METABOLITE
    assert node.label == "Glucose"


def test_reject_invalid_visual_node_identity():
    with pytest.raises(TypeError, match="EntityIdentity"):
        PathwayVisualNode(
            identity="invalid",
            node_type=GraphNodeType.METABOLITE,
            label="Glucose",
        )


def test_reject_invalid_visual_node_type():
    with pytest.raises(TypeError, match="GraphNodeType"):
        PathwayVisualNode(
            identity=EntityIdentity.generate(),
            node_type="metabolite",
            label="Glucose",
        )


@pytest.mark.parametrize(
    "label",
    [
        "",
        " ",
        " Glucose",
        "Glucose ",
        None,
        123,
    ],
)
def test_reject_invalid_visual_node_label(label):
    with pytest.raises(ValueError, match="label"):
        PathwayVisualNode(
            identity=EntityIdentity.generate(),
            node_type=GraphNodeType.METABOLITE,
            label=label,
        )


def test_create_visual_edge(glucose, reaction):
    edge = PathwayVisualEdge(
        source_identity=glucose.identity,
        target_identity=reaction.identity,
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(2),
    )

    assert edge.source_identity == glucose.identity
    assert edge.target_identity == reaction.identity
    assert edge.role is GraphEdgeRole.REACTANT
    assert edge.coefficient == Decimal(2)


def test_reject_invalid_visual_edge_identity():
    with pytest.raises(TypeError, match="source"):
        PathwayVisualEdge(
            source_identity="invalid",
            target_identity=EntityIdentity.generate(),
            role=GraphEdgeRole.REACTANT,
            coefficient=Decimal(1),
        )


def test_reject_invalid_visual_edge_role(glucose, reaction):
    with pytest.raises(TypeError, match="GraphEdgeRole"):
        PathwayVisualEdge(
            source_identity=glucose.identity,
            target_identity=reaction.identity,
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
def test_reject_non_positive_visual_edge_coefficient(
    glucose,
    reaction,
    coefficient,
):
    with pytest.raises(ValueError, match="greater than zero"):
        PathwayVisualEdge(
            source_identity=glucose.identity,
            target_identity=reaction.identity,
            role=GraphEdgeRole.REACTANT,
            coefficient=coefficient,
        )


def test_reject_non_finite_visual_edge_coefficient(glucose, reaction):
    with pytest.raises(ValueError, match="finite"):
        PathwayVisualEdge(
            source_identity=glucose.identity,
            target_identity=reaction.identity,
            role=GraphEdgeRole.REACTANT,
            coefficient=Decimal("Infinity"),
        )


def test_reject_non_decimal_visual_edge_coefficient(glucose, reaction):
    with pytest.raises(TypeError, match="Decimal"):
        PathwayVisualEdge(
            source_identity=glucose.identity,
            target_identity=reaction.identity,
            role=GraphEdgeRole.REACTANT,
            coefficient=1,
        )


def test_convert_graph_into_visualization(pathway_graph, visualization):
    assert isinstance(visualization, PathwayVisualization)
    assert visualization.pathway_identity == pathway_graph.pathway_identity


def test_visualization_preserves_node_count(pathway_graph, visualization):
    assert len(visualization.nodes) == len(pathway_graph.nodes)


def test_visualization_preserves_edge_count(pathway_graph, visualization):
    assert len(visualization.edges) == len(pathway_graph.edges)


def test_visualization_preserves_node_identities(pathway_graph, visualization):
    graph_identities = {
        node.identity
        for node in pathway_graph.nodes
    }

    visual_identities = {
        node.identity
        for node in visualization.nodes
    }

    assert visual_identities == graph_identities


def test_visualization_preserves_node_labels(visualization):
    labels = {
        node.label
        for node in visualization.nodes
    }

    assert labels == {
        "Glucose",
        "Glucose phosphorylation",
        "Glucose-6-phosphate",
    }


def test_visualization_preserves_node_types(visualization):
    assert len(visualization.metabolite_nodes) == 2
    assert len(visualization.reaction_nodes) == 1


def test_visualization_preserves_edge_directions(visualization, glucose, reaction):
    reactant_edge = visualization.edges[0]

    assert reactant_edge.source_identity == glucose.identity
    assert reactant_edge.target_identity == reaction.identity
    assert reactant_edge.role is GraphEdgeRole.REACTANT


def test_visualization_preserves_stoichiometric_coefficients():
    glucose = Metabolite(name="Glucose")
    product = Metabolite(name="Product")

    reaction = Reaction(
        name="Example reaction",
        reactants=(
            ReactionParticipant(glucose, Decimal(2)),
        ),
        products=(
            ReactionParticipant(product, Decimal("0.5")),
        ),
    )

    pathway = Pathway(
        name="Example pathway",
        reactions=(reaction,),
    )

    visualization = PathwayVisualization.from_graph(
        PathwayGraph.from_pathway(pathway)
    )

    assert visualization.edges[0].coefficient == Decimal(2)
    assert visualization.edges[1].coefficient == Decimal("0.5")


def test_reject_non_graph_visualization_source():
    with pytest.raises(TypeError, match="PathwayGraph instance"):
        PathwayVisualization.from_graph("invalid")


def test_reject_invalid_pathway_identity():
    with pytest.raises(TypeError, match="EntityIdentity"):
        PathwayVisualization(
            pathway_identity="invalid",
            nodes=(),
            edges=(),
        )


def test_reject_non_tuple_visual_nodes():
    with pytest.raises(TypeError, match="nodes"):
        PathwayVisualization(
            pathway_identity=EntityIdentity.generate(),
            nodes=[],
            edges=(),
        )


def test_reject_non_tuple_visual_edges():
    with pytest.raises(TypeError, match="edges"):
        PathwayVisualization(
            pathway_identity=EntityIdentity.generate(),
            nodes=(),
            edges=[],
        )


def test_reject_duplicate_visual_nodes():
    node = PathwayVisualNode(
        identity=EntityIdentity.generate(),
        node_type=GraphNodeType.METABOLITE,
        label="Glucose",
    )

    with pytest.raises(ValueError, match="duplicate nodes"):
        PathwayVisualization(
            pathway_identity=EntityIdentity.generate(),
            nodes=(node, node),
            edges=(),
        )


def test_reject_visual_edge_with_missing_node():
    source = PathwayVisualNode(
        identity=EntityIdentity.generate(),
        node_type=GraphNodeType.METABOLITE,
        label="Glucose",
    )

    edge = PathwayVisualEdge(
        source_identity=source.identity,
        target_identity=EntityIdentity.generate(),
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(1),
    )

    with pytest.raises(ValueError, match="does not exist"):
        PathwayVisualization(
            pathway_identity=EntityIdentity.generate(),
            nodes=(source,),
            edges=(edge,),
        )


def test_reject_invalid_reactant_visual_edge_direction():
    metabolite_identity = EntityIdentity.generate()
    reaction_identity = EntityIdentity.generate()

    metabolite_node = PathwayVisualNode(
        identity=metabolite_identity,
        node_type=GraphNodeType.METABOLITE,
        label="Glucose",
    )

    reaction_node = PathwayVisualNode(
        identity=reaction_identity,
        node_type=GraphNodeType.REACTION,
        label="Phosphorylation",
    )

    edge = PathwayVisualEdge(
        source_identity=reaction_identity,
        target_identity=metabolite_identity,
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(1),
    )

    with pytest.raises(ValueError, match="Invalid direction"):
        PathwayVisualization(
            pathway_identity=EntityIdentity.generate(),
            nodes=(metabolite_node, reaction_node),
            edges=(edge,),
        )


def test_reject_duplicate_visual_edges():
    metabolite_identity = EntityIdentity.generate()
    reaction_identity = EntityIdentity.generate()

    nodes = (
        PathwayVisualNode(
            identity=metabolite_identity,
            node_type=GraphNodeType.METABOLITE,
            label="Glucose",
        ),
        PathwayVisualNode(
            identity=reaction_identity,
            node_type=GraphNodeType.REACTION,
            label="Phosphorylation",
        ),
    )

    edge = PathwayVisualEdge(
        source_identity=metabolite_identity,
        target_identity=reaction_identity,
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(1),
    )

    with pytest.raises(ValueError, match="duplicate edges"):
        PathwayVisualization(
            pathway_identity=EntityIdentity.generate(),
            nodes=nodes,
            edges=(edge, edge),
        )
