
from decimal import Decimal

import pytest

from aditi.api import (
    PathwayAPIService,
    PathwaySceneResponse,
)
from aditi.domain.pathways import (
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

    return PathwayGraph.from_pathway(pathway)


def test_api_service_initializes_with_default_visualization_service() -> None:
    service = PathwayAPIService()

    assert service.available_layouts == (
        "hierarchical",
        "force-directed",
    )


def test_api_service_accepts_custom_visualization_service() -> None:
    visualization_service = PathwayVisualizationService()

    service = PathwayAPIService(
        visualization_service=visualization_service
    )

    assert service.available_layouts == (
        "hierarchical",
        "force-directed",
    )


def test_api_service_rejects_invalid_visualization_service() -> None:
    with pytest.raises(TypeError):
        PathwayAPIService(
            visualization_service="invalid"
        )


def test_api_service_creates_default_visualization_response() -> None:
    service = PathwayAPIService()
    graph = create_pathway_graph()

    response = service.create_visualization(graph)

    assert isinstance(response, PathwaySceneResponse)
    assert response.pathway_identity == graph.pathway_identity.value
    assert len(response.nodes) == len(graph.nodes)
    assert len(response.edges) == len(graph.edges)


@pytest.mark.parametrize(
    "layout_id",
    [
        "hierarchical",
        "force-directed",
    ],
)
def test_api_service_supports_registered_layouts(
    layout_id: str,
) -> None:
    service = PathwayAPIService()

    response = service.create_visualization(
        create_pathway_graph(),
        layout_id=layout_id,
    )

    assert isinstance(response, PathwaySceneResponse)


def test_api_service_preserves_node_identities() -> None:
    service = PathwayAPIService()
    graph = create_pathway_graph()

    response = service.create_visualization(graph)

    assert {
        node.identity
        for node in response.nodes
    } == {
        node.identity.value
        for node in graph.nodes
    }


def test_api_service_preserves_edge_coefficients() -> None:
    service = PathwayAPIService()

    response = service.create_visualization(
        create_pathway_graph()
    )

    assert all(
        edge.coefficient == Decimal(1)
        for edge in response.edges
    )


def test_api_service_response_is_json_serializable() -> None:
    service = PathwayAPIService()

    response = service.create_visualization(
        create_pathway_graph()
    )

    payload = response.model_dump(mode="json")

    assert isinstance(payload, dict)
    assert isinstance(payload["pathway_identity"], str)
    assert isinstance(payload["nodes"], list)
    assert isinstance(payload["edges"], list)


def test_api_service_rejects_invalid_pathway_graph() -> None:
    service = PathwayAPIService()

    with pytest.raises(TypeError):
        service.create_visualization("invalid")


def test_api_service_propagates_unknown_layout_error() -> None:
    service = PathwayAPIService()

    with pytest.raises(RuntimeError):
        service.create_visualization(
            create_pathway_graph(),
            layout_id="unknown",
        )


def test_api_service_can_create_multiple_visualizations() -> None:
    service = PathwayAPIService()

    first_graph = create_pathway_graph()
    second_graph = create_pathway_graph()

    first_response = service.create_visualization(first_graph)
    second_response = service.create_visualization(second_graph)

    assert first_response.pathway_identity == first_graph.pathway_identity.value
    assert second_response.pathway_identity == second_graph.pathway_identity.value

    assert (
        first_response.pathway_identity
        != second_response.pathway_identity
    )
