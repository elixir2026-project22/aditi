
from decimal import Decimal

import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways import (
    Metabolite,
    Pathway,
    PathwayGraph,
    Reaction,
    ReactionParticipant,
)
from aditi.visualization.pathways import PathwayVisualization
from aditi.visualization.pathways.layouts import (
    HierarchicalLayout,
    NodePosition,
    PathwayLayout,
)


def create_linear_visualization() -> PathwayVisualization:
    glucose = Metabolite(name="Glucose")
    glucose_6_phosphate = Metabolite(
        name="Glucose-6-phosphate"
    )

    reaction = Reaction(
        name="Glucose phosphorylation",
        reactants=(
            ReactionParticipant(
                glucose,
                Decimal(1),
            ),
        ),
        products=(
            ReactionParticipant(
                glucose_6_phosphate,
                Decimal(1),
            ),
        ),
    )

    pathway = Pathway(
        name="Glycolysis",
        reactions=(reaction,),
    )

    return PathwayVisualization.from_graph(
        PathwayGraph.from_pathway(pathway)
    )


def create_cyclic_visualization() -> PathwayVisualization:
    metabolite_a = Metabolite(name="Metabolite A")
    metabolite_b = Metabolite(name="Metabolite B")

    reaction_a = Reaction(
        name="Reaction A",
        reactants=(
            ReactionParticipant(metabolite_a),
        ),
        products=(
            ReactionParticipant(metabolite_b),
        ),
    )

    reaction_b = Reaction(
        name="Reaction B",
        reactants=(
            ReactionParticipant(metabolite_b),
        ),
        products=(
            ReactionParticipant(metabolite_a),
        ),
    )

    pathway = Pathway(
        name="Cyclic pathway",
        reactions=(
            reaction_a,
            reaction_b,
        ),
    )

    return PathwayVisualization.from_graph(
        PathwayGraph.from_pathway(pathway)
    )


def test_hierarchical_layout_positions_all_nodes() -> None:
    visualization = create_linear_visualization()

    layout = HierarchicalLayout().calculate(
        visualization
    )

    assert layout.pathway_identity == visualization.pathway_identity

    assert len(layout.positions) == len(visualization.nodes)

    assert {
        position.identity
        for position in layout.positions
    } == {
        node.identity
        for node in visualization.nodes
    }


def test_hierarchical_layout_places_nodes_left_to_right() -> None:
    visualization = create_linear_visualization()

    layout = HierarchicalLayout().calculate(
        visualization
    )

    metabolite = visualization.metabolite_nodes[0]
    reaction = visualization.reaction_nodes[0]
    product = visualization.metabolite_nodes[1]

    metabolite_position = layout.get_position(
        metabolite.identity
    )

    reaction_position = layout.get_position(
        reaction.identity
    )

    product_position = layout.get_position(
        product.identity
    )

    assert metabolite_position is not None
    assert reaction_position is not None
    assert product_position is not None

    assert metabolite_position.x < reaction_position.x
    assert reaction_position.x < product_position.x


def test_hierarchical_layout_uses_configured_spacing() -> None:
    visualization = create_linear_visualization()

    layout = HierarchicalLayout(
        horizontal_spacing=300,
        vertical_spacing=150,
    ).calculate(visualization)

    x_coordinates = sorted(
        {
            position.x
            for position in layout.positions
        }
    )

    assert x_coordinates == [
        0,
        300,
        600,
    ]


def test_hierarchical_layout_is_deterministic() -> None:
    visualization = create_linear_visualization()

    algorithm = HierarchicalLayout()

    first = algorithm.calculate(visualization)
    second = algorithm.calculate(visualization)

    assert first == second


def test_hierarchical_layout_centers_single_layer() -> None:
    visualization = create_cyclic_visualization()

    layout = HierarchicalLayout().calculate(
        visualization
    )

    assert len(
        {
            position.x
            for position in layout.positions
        }
    ) == 1

    y_coordinates = [
        position.y
        for position in layout.positions
    ]

    assert sum(y_coordinates) == pytest.approx(0)


def test_hierarchical_layout_handles_cycles() -> None:
    visualization = create_cyclic_visualization()

    layout = HierarchicalLayout().calculate(
        visualization
    )

    assert len(layout.positions) == len(visualization.nodes)

    assert all(
        isinstance(position, NodePosition)
        for position in layout.positions
    )


def test_layout_returns_position_by_identity() -> None:
    visualization = create_linear_visualization()

    layout = HierarchicalLayout().calculate(
        visualization
    )

    identity = visualization.nodes[0].identity

    position = layout.get_position(identity)

    assert position is not None
    assert position.identity == identity


def test_layout_returns_none_for_unknown_identity() -> None:
    layout = HierarchicalLayout().calculate(
        create_linear_visualization()
    )

    assert layout.get_position(
        EntityIdentity.generate()
    ) is None


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        float("inf"),
        float("-inf"),
        float("nan"),
    ],
)
def test_layout_rejects_invalid_spacing(value: float) -> None:
    with pytest.raises(ValueError):
        HierarchicalLayout(horizontal_spacing=value)


@pytest.mark.parametrize(
    "value",
    [
        True,
        "100",
        None,
    ],
)
def test_layout_rejects_non_numeric_spacing(value: object) -> None:
    with pytest.raises(TypeError):
        HierarchicalLayout(horizontal_spacing=value)


def test_node_position_rejects_invalid_coordinates() -> None:
    identity = EntityIdentity.generate()

    with pytest.raises(ValueError):
        NodePosition(
            identity=identity,
            x=float("nan"),
            y=0,
        )


def test_node_position_rejects_boolean_coordinates() -> None:
    with pytest.raises(TypeError):
        NodePosition(
            identity=EntityIdentity.generate(),
            x=True,
            y=0,
        )


def test_pathway_layout_rejects_duplicate_positions() -> None:
    identity = EntityIdentity.generate()

    position = NodePosition(
        identity=identity,
        x=0,
        y=0,
    )

    with pytest.raises(ValueError):
        PathwayLayout(
            pathway_identity=EntityIdentity.generate(),
            positions=(
                position,
                position,
            ),
        )


def test_layout_rejects_invalid_visualization() -> None:
    with pytest.raises(TypeError):
        HierarchicalLayout().calculate("invalid")
