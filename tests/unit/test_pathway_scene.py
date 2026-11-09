
from decimal import Decimal

import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways import (
    GraphEdgeRole,
    Metabolite,
    Pathway,
    PathwayGraph,
    Reaction,
    ReactionParticipant,
)
from aditi.visualization.pathways import (
    PathwayScene,
    PathwaySceneNode,
    PathwayVisualEdge,
    PathwayVisualization,
    SceneBounds,
)
from aditi.visualization.pathways.layouts import (
    HierarchicalLayout,
    NodePosition,
    PathwayLayout,
)


def create_visualization() -> PathwayVisualization:
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


def create_scene(
    visualization: PathwayVisualization | None = None,
) -> PathwayScene:
    if visualization is None:
        visualization = create_visualization()

    layout = HierarchicalLayout().calculate(visualization)

    return PathwayScene.from_models(
        visualization,
        layout,
    )


def test_scene_combines_visualization_and_layout() -> None:
    visualization = create_visualization()
    scene = create_scene(visualization)

    assert scene.pathway_identity == visualization.pathway_identity
    assert len(scene.nodes) == len(visualization.nodes)
    assert scene.edges == visualization.edges


def test_scene_preserves_node_identities() -> None:
    visualization = create_visualization()
    scene = create_scene(visualization)

    assert {
        node.identity
        for node in scene.nodes
    } == {
        node.identity
        for node in visualization.nodes
    }


def test_scene_preserves_node_labels_and_types() -> None:
    visualization = create_visualization()
    scene = create_scene(visualization)

    for scene_node, visual_node in zip(
        scene.nodes,
        visualization.nodes,
        strict=True,
    ):
        assert scene_node.identity == visual_node.identity
        assert scene_node.label == visual_node.label
        assert scene_node.node_type == visual_node.node_type


def test_scene_preserves_calculated_positions() -> None:
    visualization = create_visualization()
    layout = HierarchicalLayout().calculate(visualization)

    scene = PathwayScene.from_models(
        visualization,
        layout,
    )

    for scene_node in scene.nodes:
        position = layout.get_position(scene_node.identity)

        assert position is not None
        assert scene_node.x == position.x
        assert scene_node.y == position.y


def test_scene_separates_metabolite_and_reaction_nodes() -> None:
    scene = create_scene()

    assert len(scene.metabolite_nodes) == 2
    assert len(scene.reaction_nodes) == 1


def test_scene_calculates_bounds() -> None:
    scene = create_scene()

    bounds = scene.bounds

    assert bounds is not None
    assert bounds.min_x == 0
    assert bounds.max_x == 480
    assert bounds.width == 480
    assert bounds.height >= 0


def test_scene_bounds_returns_none_for_empty_scene() -> None:
    scene = PathwayScene(
        pathway_identity=EntityIdentity.generate(),
        nodes=(),
        edges=(),
    )

    assert scene.bounds is None


def test_scene_node_exposes_position_and_visual_properties() -> None:
    scene = create_scene()
    node = scene.nodes[0]

    assert node.identity == node.visual_node.identity
    assert node.label == node.visual_node.label
    assert node.node_type == node.visual_node.node_type
    assert node.x == node.position.x
    assert node.y == node.position.y


def test_scene_can_retrieve_node_by_identity() -> None:
    scene = create_scene()
    identity = scene.nodes[0].identity

    node = scene.get_node(identity)

    assert node is not None
    assert node.identity == identity


def test_scene_returns_none_for_unknown_identity() -> None:
    scene = create_scene()

    assert scene.get_node(
        EntityIdentity.generate()
    ) is None


def test_scene_rejects_mismatched_pathway_identity() -> None:
    visualization = create_visualization()
    layout = HierarchicalLayout().calculate(visualization)

    invalid_layout = PathwayLayout(
        pathway_identity=EntityIdentity.generate(),
        positions=layout.positions,
    )

    with pytest.raises(ValueError):
        PathwayScene.from_models(
            visualization,
            invalid_layout,
        )


def test_scene_rejects_missing_layout_positions() -> None:
    visualization = create_visualization()
    layout = HierarchicalLayout().calculate(visualization)

    incomplete_layout = PathwayLayout(
        pathway_identity=layout.pathway_identity,
        positions=layout.positions[:-1],
    )

    with pytest.raises(ValueError):
        PathwayScene.from_models(
            visualization,
            incomplete_layout,
        )


def test_scene_rejects_additional_layout_positions() -> None:
    visualization = create_visualization()
    layout = HierarchicalLayout().calculate(visualization)

    additional_position = NodePosition(
        identity=EntityIdentity.generate(),
        x=0,
        y=0,
    )

    invalid_layout = PathwayLayout(
        pathway_identity=layout.pathway_identity,
        positions=(
            *layout.positions,
            additional_position,
        ),
    )

    with pytest.raises(ValueError):
        PathwayScene.from_models(
            visualization,
            invalid_layout,
        )


def test_scene_rejects_invalid_visualization() -> None:
    layout = HierarchicalLayout().calculate(
        create_visualization()
    )

    with pytest.raises(TypeError):
        PathwayScene.from_models(
            "invalid",
            layout,
        )


def test_scene_rejects_invalid_layout() -> None:
    visualization = create_visualization()

    with pytest.raises(TypeError):
        PathwayScene.from_models(
            visualization,
            "invalid",
        )


def test_scene_rejects_node_with_mismatched_identity() -> None:
    scene = create_scene()
    node = scene.nodes[0]

    invalid_position = NodePosition(
        identity=EntityIdentity.generate(),
        x=node.x,
        y=node.y,
    )

    with pytest.raises(ValueError):
        PathwaySceneNode(
            visual_node=node.visual_node,
            position=invalid_position,
        )


def test_scene_rejects_missing_edge_endpoint() -> None:
    scene = create_scene()

    invalid_edge = PathwayVisualEdge(
        source_identity=EntityIdentity.generate(),
        target_identity=scene.nodes[0].identity,
        role=GraphEdgeRole.REACTANT,
        coefficient=Decimal(1),
    )

    with pytest.raises(ValueError):
        PathwayScene(
            pathway_identity=scene.pathway_identity,
            nodes=scene.nodes,
            edges=(invalid_edge,),
        )


def test_scene_bounds_reject_invalid_coordinates() -> None:
    with pytest.raises(ValueError):
        SceneBounds(
            min_x=0,
            min_y=0,
            max_x=float("inf"),
            max_y=10,
        )


def test_scene_bounds_reject_inverted_ranges() -> None:
    with pytest.raises(ValueError):
        SceneBounds(
            min_x=10,
            min_y=0,
            max_x=0,
            max_y=10,
        )


def test_scene_is_immutable() -> None:
    scene = create_scene()

    with pytest.raises(AttributeError):
        scene.nodes = ()
