
from decimal import Decimal

import pytest

from aditi.domain.pathways import (
    Metabolite,
    Pathway,
    PathwayGraph,
    Reaction,
    ReactionParticipant,
)
from aditi.visualization.pathways import (
    PathwayScene,
    PathwayVisualizationService,
)
from aditi.visualization.pathways.layouts import (
    ForceDirectedLayout,
    HierarchicalLayout,
    LayoutRegistryError,
    PathwayLayoutRegistry,
)


def create_pathway_graph() -> PathwayGraph:
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
        name="Glycolysis",
        reactions=(
            reaction_a,
            reaction_b,
        ),
    )

    return PathwayGraph.from_pathway(pathway)


def create_custom_registry() -> PathwayLayoutRegistry:
    registry = PathwayLayoutRegistry()

    registry.register(
        "hierarchical",
        HierarchicalLayout(),
    )

    registry.register(
        "force-directed",
        ForceDirectedLayout(),
    )

    return registry


def test_service_initializes_with_default_registry() -> None:
    service = PathwayVisualizationService()

    assert service.available_layouts == (
        "hierarchical",
        "force-directed",
    )


def test_service_accepts_custom_registry() -> None:
    registry = create_custom_registry()

    service = PathwayVisualizationService(
        layout_registry=registry
    )

    assert service.available_layouts == registry.available_layouts


def test_service_rejects_invalid_registry() -> None:
    with pytest.raises(TypeError):
        PathwayVisualizationService(
            layout_registry="invalid"
        )


def test_service_creates_scene_with_default_layout() -> None:
    service = PathwayVisualizationService()
    graph = create_pathway_graph()

    scene = service.create_scene(graph)

    assert isinstance(scene, PathwayScene)
    assert scene.pathway_identity == graph.pathway_identity
    assert len(scene.nodes) == len(graph.nodes)
    assert len(scene.edges) == len(graph.edges)


def test_service_creates_scene_with_hierarchical_layout() -> None:
    service = PathwayVisualizationService()
    graph = create_pathway_graph()

    scene = service.create_scene(
        graph,
        layout_id="hierarchical",
    )

    assert isinstance(scene, PathwayScene)
    assert len(scene.nodes) == len(graph.nodes)


def test_service_creates_scene_with_force_directed_layout() -> None:
    service = PathwayVisualizationService()
    graph = create_pathway_graph()

    scene = service.create_scene(
        graph,
        layout_id="force-directed",
    )

    assert isinstance(scene, PathwayScene)
    assert len(scene.nodes) == len(graph.nodes)


def test_service_preserves_graph_node_identities() -> None:
    service = PathwayVisualizationService()
    graph = create_pathway_graph()

    scene = service.create_scene(graph)

    assert {
        node.identity
        for node in scene.nodes
    } == {
        node.identity
        for node in graph.nodes
    }


def test_service_preserves_graph_edges() -> None:
    service = PathwayVisualizationService()
    graph = create_pathway_graph()

    scene = service.create_scene(graph)

    assert scene.edges == tuple(
        scene.edges
    )

    assert len(scene.edges) == len(graph.edges)


def test_service_creates_scene_with_positions() -> None:
    service = PathwayVisualizationService()
    graph = create_pathway_graph()

    scene = service.create_scene(graph)

    assert all(
        isinstance(node.x, float)
        and isinstance(node.y, float)
        for node in scene.nodes
    )


def test_service_creates_scene_bounds() -> None:
    service = PathwayVisualizationService()
    graph = create_pathway_graph()

    scene = service.create_scene(graph)

    assert scene.bounds is not None
    assert scene.bounds.width >= 0
    assert scene.bounds.height >= 0


def test_service_rejects_unknown_layout() -> None:
    service = PathwayVisualizationService()

    with pytest.raises(LayoutRegistryError):
        service.create_scene(
            create_pathway_graph(),
            layout_id="unknown",
        )


def test_service_rejects_invalid_graph() -> None:
    service = PathwayVisualizationService()

    with pytest.raises(TypeError):
        service.create_scene("invalid")


def test_service_can_reuse_registry() -> None:
    registry = create_custom_registry()

    first_service = PathwayVisualizationService(registry)
    second_service = PathwayVisualizationService(registry)

    assert first_service.available_layouts == (
        second_service.available_layouts
    )


def test_service_can_create_multiple_scenes() -> None:
    service = PathwayVisualizationService()
    first_graph = create_pathway_graph()
    second_graph = create_pathway_graph()

    first_scene = service.create_scene(first_graph)
    second_scene = service.create_scene(second_graph)

    assert first_scene.pathway_identity == first_graph.pathway_identity
    assert second_scene.pathway_identity == second_graph.pathway_identity

    assert first_scene.pathway_identity != second_scene.pathway_identity
