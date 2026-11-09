
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from aditi.api.schemas import (
    PathwaySceneBoundsSchema,
    PathwaySceneEdgeSchema,
    PathwaySceneNodeSchema,
    PathwaySceneResponse,
)
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
    PathwayVisualizationService,
)


def create_pathway_graph() -> PathwayGraph:
    glucose = Metabolite(name="Glucose")
    glucose_6_phosphate = Metabolite(
        name="Glucose-6-phosphate"
    )

    reaction = Reaction(
        name="Glucose phosphorylation",
        reactants=(
            ReactionParticipant(
                glucose,
                Decimal(2),
            ),
        ),
        products=(
            ReactionParticipant(
                glucose_6_phosphate,
                Decimal(2),
            ),
        ),
    )

    pathway = Pathway(
        name="Glycolysis",
        reactions=(reaction,),
    )

    return PathwayGraph.from_pathway(pathway)


def create_response() -> PathwaySceneResponse:
    graph = create_pathway_graph()

    scene = PathwayVisualizationService().create_scene(
        graph,
        layout_id="hierarchical",
    )

    return PathwaySceneResponse.from_scene(scene)


def test_response_converts_pathway_identity() -> None:
    response = create_response()

    assert isinstance(response.pathway_identity, UUID)


def test_response_contains_all_scene_nodes() -> None:
    graph = create_pathway_graph()
    scene = PathwayVisualizationService().create_scene(graph)

    response = PathwaySceneResponse.from_scene(scene)

    assert len(response.nodes) == len(scene.nodes)


def test_response_contains_all_scene_edges() -> None:
    graph = create_pathway_graph()
    scene = PathwayVisualizationService().create_scene(graph)

    response = PathwaySceneResponse.from_scene(scene)

    assert len(response.edges) == len(scene.edges)


def test_response_preserves_node_identity() -> None:
    graph = create_pathway_graph()
    scene = PathwayVisualizationService().create_scene(graph)

    response = PathwaySceneResponse.from_scene(scene)

    assert {
        node.identity
        for node in response.nodes
    } == {
        node.identity.value
        for node in scene.nodes
    }


def test_response_preserves_node_labels_and_types() -> None:
    response = create_response()

    assert {
        (node.label, node.node_type)
        for node in response.nodes
    } == {
        ("Glucose", GraphNodeType.METABOLITE),
        ("Glucose-6-phosphate", GraphNodeType.METABOLITE),
        ("Glucose phosphorylation", GraphNodeType.REACTION),
    }


def test_response_preserves_node_positions() -> None:
    graph = create_pathway_graph()
    scene = PathwayVisualizationService().create_scene(graph)

    response = PathwaySceneResponse.from_scene(scene)

    for api_node, scene_node in zip(
        response.nodes,
        scene.nodes,
        strict=True,
    ):
        assert api_node.identity == scene_node.identity.value
        assert api_node.x == scene_node.x
        assert api_node.y == scene_node.y


def test_response_preserves_edge_direction_and_coefficient() -> None:
    response = create_response()

    assert all(
        edge.role in (
            GraphEdgeRole.REACTANT,
            GraphEdgeRole.PRODUCT,
        )
        for edge in response.edges
    )

    assert all(
        edge.coefficient == Decimal(2)
        for edge in response.edges
    )


def test_response_contains_scene_bounds() -> None:
    response = create_response()

    assert response.bounds is not None
    assert response.bounds.width >= 0
    assert response.bounds.height >= 0


def test_response_bounds_match_scene() -> None:
    graph = create_pathway_graph()
    scene = PathwayVisualizationService().create_scene(graph)

    response = PathwaySceneResponse.from_scene(scene)

    assert scene.bounds is not None
    assert response.bounds is not None

    assert response.bounds.min_x == scene.bounds.min_x
    assert response.bounds.min_y == scene.bounds.min_y
    assert response.bounds.max_x == scene.bounds.max_x
    assert response.bounds.max_y == scene.bounds.max_y


def test_response_is_json_serializable() -> None:
    response = create_response()

    payload = response.model_dump(mode="json")

    assert isinstance(payload, dict)
    assert isinstance(payload["pathway_identity"], str)
    assert isinstance(payload["nodes"], list)
    assert isinstance(payload["edges"], list)


def test_response_serializes_decimal_coefficients_without_float_conversion() -> None:
    response = create_response()

    payload = response.model_dump(mode="json")

    assert all(
        edge["coefficient"] == "2"
        for edge in payload["edges"]
    )


def test_response_rejects_invalid_scene() -> None:
    with pytest.raises(TypeError):
        PathwaySceneResponse.from_scene("invalid")


def test_node_schema_rejects_empty_label() -> None:
    with pytest.raises(ValidationError):
        PathwaySceneNodeSchema(
            identity=UUID(int=1),
            node_type=GraphNodeType.METABOLITE,
            label="",
            x=0.0,
            y=0.0,
        )


def test_node_schema_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        PathwaySceneNodeSchema(
            identity=UUID(int=1),
            node_type=GraphNodeType.METABOLITE,
            label="Glucose",
            x=0.0,
            y=0.0,
            unexpected="value",
        )


def test_edge_schema_rejects_non_positive_coefficient() -> None:
    with pytest.raises(ValidationError):
        PathwaySceneEdgeSchema(
            source_identity=UUID(int=1),
            target_identity=UUID(int=2),
            role=GraphEdgeRole.REACTANT,
            coefficient=Decimal(0),
        )


def test_bounds_schema_rejects_negative_dimensions() -> None:
    with pytest.raises(ValidationError):
        PathwaySceneBoundsSchema(
            min_x=0.0,
            min_y=0.0,
            max_x=10.0,
            max_y=10.0,
            width=-10.0,
            height=10.0,
        )


def test_response_schema_is_immutable() -> None:
    response = create_response()

    with pytest.raises(ValidationError):
        response.nodes = ()
