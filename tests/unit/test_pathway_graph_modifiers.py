
from decimal import Decimal

from aditi.domain.pathways.graph import (
    GraphEdgeRole,
    GraphNodeType,
    PathwayGraph,
)
from aditi.domain.pathways.metabolite import Metabolite
from aditi.domain.pathways.pathway import Pathway
from aditi.domain.pathways.reaction import (
    Reaction,
    ReactionParticipant,
)


def make_pathway() -> tuple[Pathway, Reaction, Metabolite]:
    glucose = Metabolite(name="Glucose")
    fructose = Metabolite(name="Fructose")

    reaction = Reaction(
        name="Glucose Isomerization",
        reactants=(
            ReactionParticipant(
                metabolite=glucose,
                coefficient=Decimal("1"),
            ),
        ),
        products=(
            ReactionParticipant(
                metabolite=fructose,
                coefficient=Decimal("1"),
            ),
        ),
        modifiers=(
            ReactionParticipant(
                metabolite=glucose,
                coefficient=Decimal("1"),
            ),
        ),
    )

    pathway = Pathway(
        name="Modifier Test Pathway",
        reactions=(reaction,),
    )

    return pathway, reaction, glucose


def test_graph_creates_modifier_edge() -> None:
    pathway, reaction, glucose = make_pathway()

    graph = PathwayGraph.from_pathway(pathway)

    modifier_edges = [
        edge
        for edge in graph.edges
        if edge.role is GraphEdgeRole.MODIFIER
    ]

    assert len(modifier_edges) == 1

    edge = modifier_edges[0]

    assert edge.source_identity == glucose.identity
    assert edge.target_identity == reaction.identity
    assert edge.coefficient == Decimal("1")


def test_modifier_and_reactant_edges_remain_distinct() -> None:
    pathway, reaction, glucose = make_pathway()

    graph = PathwayGraph.from_pathway(pathway)

    glucose_edges = [
        edge
        for edge in graph.edges
        if edge.source_identity == glucose.identity
        and edge.target_identity == reaction.identity
    ]

    assert len(glucose_edges) == 2

    assert {
        edge.role for edge in glucose_edges
    } == {
        GraphEdgeRole.REACTANT,
        GraphEdgeRole.MODIFIER,
    }


def test_modifier_does_not_create_duplicate_graph_nodes() -> None:
    pathway, _, _ = make_pathway()

    graph = PathwayGraph.from_pathway(pathway)

    assert len(graph.metabolite_nodes) == 2
    assert len(graph.reaction_nodes) == 1

    glucose_nodes = [
        node
        for node in graph.metabolite_nodes
        if node.entity.name == "Glucose"
    ]

    assert len(glucose_nodes) == 1


def test_modifier_edge_has_metabolite_to_reaction_direction() -> None:
    pathway, _, _ = make_pathway()

    graph = PathwayGraph.from_pathway(pathway)

    for edge in graph.edges:
        if edge.role is not GraphEdgeRole.MODIFIER:
            continue

        source = next(
            node for node in graph.nodes
            if node.identity == edge.source_identity
        )
        target = next(
            node for node in graph.nodes
            if node.identity == edge.target_identity
        )

        assert source.node_type is GraphNodeType.METABOLITE
        assert target.node_type is GraphNodeType.REACTION
