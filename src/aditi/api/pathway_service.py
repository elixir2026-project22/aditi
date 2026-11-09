
from aditi.api.schemas import PathwaySceneResponse
from aditi.domain.pathways.graph import PathwayGraph
from aditi.visualization.pathways import (
    PathwayVisualizationService,
)


class PathwayAPIService:
    """
    Application-facing service for pathway visualization requests.

    Coordinates the visualization core and converts its output
    into API response models.

    This service does not depend on FastAPI or HTTP request objects.
    """

    def __init__(
        self,
        visualization_service: PathwayVisualizationService | None = None,
    ) -> None:
        if (
            visualization_service is not None
            and not isinstance(
                visualization_service,
                PathwayVisualizationService,
            )
        ):
            raise TypeError(
                "Visualization service must be a "
                "PathwayVisualizationService."
            )

        self._visualization_service = (
            visualization_service
            if visualization_service is not None
            else PathwayVisualizationService()
        )

    @property
    def available_layouts(self) -> tuple[str, ...]:
        """Return the layout algorithms available to API clients."""

        return self._visualization_service.available_layouts

    def create_visualization(
        self,
        pathway_graph: PathwayGraph,
        layout_id: str = "hierarchical",
    ) -> PathwaySceneResponse:
        """
        Generate a pathway visualization API response.

        The method delegates scene construction to the visualization
        service and converts the resulting scene into a Pydantic
        response model.
        """

        if not isinstance(pathway_graph, PathwayGraph):
            raise TypeError(
                "Pathway API service requires a PathwayGraph."
            )

        scene = self._visualization_service.create_scene(
            pathway_graph,
            layout_id=layout_id,
        )

        return PathwaySceneResponse.from_scene(scene)
