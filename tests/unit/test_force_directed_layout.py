
from decimal import Decimal

import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways import (
    GraphNodeType,
    Metabolite,
    Pathway,
    PathwayGraph,
    Reaction,
    ReactionParticipant,
)
from aditi.visualization.pathways.layouts import (
    ForceDirectedLayout,
    PathwayLayout,
)
from aditi.visualization.pathways.model import (
    PathwayVisualization,
    PathwayVisualNode,
)


def create_visualization() -> PathwayVisualization:
    glucose = Metabolite(name="Glucose")
    glucose_6_phosphate = Metabolite(
        name="Glucose-6-phosphate"
    )
    fructose_6_phosphate = Metabolite(
        name="Fructose-6-phosphate"
    )

    reaction_a = Reaction(
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

    reaction_b = Reaction(
        name="Phosphoglucose isomerization",
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

    pathway = Pathway(
        name="Example pathway",
        reactions=(
            reaction_a,
            reaction_b,
        ),
    )

    return PathwayVisualization.from_graph(
        PathwayGraph.from_pathway(pathway)
    )


def create_single_node_visualization() -> PathwayVisualization:
    return PathwayVisualization(
        pathway_identity=EntityIdentity.generate(),
        nodes=(
            PathwayVisualNode(
                identity=EntityIdentity.generate(),
                node_type=GraphNodeType.METABOLITE,
                label="Glucose",
            ),
        ),
        edges=(),
    )


def create_empty_visualization() -> PathwayVisualization:
    return PathwayVisualization(
        pathway_identity=EntityIdentity.generate(),
        nodes=(),
        edges=(),
    )


def test_force_directed_layout_positions_all_nodes() -> None:
    visualization = create_visualization()

    layout = ForceDirectedLayout().calculate(
        visualization
    )

    assert isinstance(layout, PathwayLayout)
    assert layout.pathway_identity == visualization.pathway_identity
    assert len(layout.positions) == len(visualization.nodes)

    assert {
        position.identity
        for position in layout.positions
    } == {
        node.identity
        for node in visualization.nodes
    }


def test_force_directed_layout_preserves_node_order() -> None:
    visualization = create_visualization()

    layout = ForceDirectedLayout().calculate(
        visualization
    )

    assert tuple(
        position.identity
        for position in layout.positions
    ) == tuple(
        node.identity
        for node in visualization.nodes
    )


def test_force_directed_layout_is_deterministic() -> None:
    visualization = create_visualization()
    algorithm = ForceDirectedLayout()

    first = algorithm.calculate(visualization)
    second = algorithm.calculate(visualization)

    assert first == second


def test_force_directed_layout_produces_finite_coordinates() -> None:
    visualization = create_visualization()

    layout = ForceDirectedLayout().calculate(
        visualization
    )

    for position in layout.positions:
        assert isinstance(position.x, float)
        assert isinstance(position.y, float)

        assert position.x == pytest.approx(position.x)
        assert position.y == pytest.approx(position.y)


def test_force_directed_layout_respects_scene_dimensions() -> None:
    width = 600.0
    height = 400.0

    layout = ForceDirectedLayout(
        width=width,
        height=height,
    ).calculate(create_visualization())

    for position in layout.positions:
        assert -width / 2 <= position.x <= width / 2
        assert -height / 2 <= position.y <= height / 2


def test_force_directed_layout_handles_single_node() -> None:
    visualization = create_single_node_visualization()

    layout = ForceDirectedLayout().calculate(
        visualization
    )

    assert len(layout.positions) == 1
    assert layout.positions[0].x == 0.0
    assert layout.positions[0].y == 0.0


def test_force_directed_layout_handles_empty_visualization() -> None:
    visualization = create_empty_visualization()

    layout = ForceDirectedLayout().calculate(
        visualization
    )

    assert layout.pathway_identity == visualization.pathway_identity
    assert layout.positions == ()


def test_force_directed_layout_supports_custom_iterations() -> None:
    visualization = create_visualization()

    layout = ForceDirectedLayout(
        iterations=10,
    ).calculate(visualization)

    assert len(layout.positions) == len(visualization.nodes)


def test_force_directed_layout_supports_zero_gravity() -> None:
    visualization = create_visualization()

    layout = ForceDirectedLayout(
        gravity=0.0,
    ).calculate(visualization)

    assert len(layout.positions) == len(visualization.nodes)


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
def test_force_directed_layout_rejects_invalid_dimensions(
    value: float,
) -> None:
    with pytest.raises(ValueError):
        ForceDirectedLayout(width=value)


@pytest.mark.parametrize(
    "value",
    [
        True,
        "100",
        None,
    ],
)
def test_force_directed_layout_rejects_non_numeric_dimensions(
    value: object,
) -> None:
    with pytest.raises(TypeError):
        ForceDirectedLayout(width=value)


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
    ],
)
def test_force_directed_layout_rejects_invalid_iterations(
    value: int,
) -> None:
    with pytest.raises(ValueError):
        ForceDirectedLayout(iterations=value)


@pytest.mark.parametrize(
    "value",
    [
        True,
        1.5,
        "100",
        None,
    ],
)
def test_force_directed_layout_rejects_non_integer_iterations(
    value: object,
) -> None:
    with pytest.raises(TypeError):
        ForceDirectedLayout(iterations=value)


@pytest.mark.parametrize(
    "value",
    [
        -1,
        float("inf"),
        float("-inf"),
        float("nan"),
    ],
)
def test_force_directed_layout_rejects_invalid_gravity(
    value: float,
) -> None:
    with pytest.raises(ValueError):
        ForceDirectedLayout(gravity=value)


@pytest.mark.parametrize(
    "value",
    [
        True,
        "0.05",
        None,
    ],
)
def test_force_directed_layout_rejects_non_numeric_gravity(
    value: object,
) -> None:
    with pytest.raises(TypeError):
        ForceDirectedLayout(gravity=value)


def test_force_directed_layout_rejects_invalid_visualization() -> None:
    with pytest.raises(TypeError):
        ForceDirectedLayout().calculate("invalid")
