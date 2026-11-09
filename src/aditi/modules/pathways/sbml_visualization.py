
from aditi.data.importers.sbml import SBMLImportService
from aditi.domain.pathways.graph import PathwayGraph
from aditi.visualization.pathways.scene import PathwayScene
from aditi.visualization.pathways.service import PathwayVisualizationService


class SBMLVisualizationWorkflow:
    """
    Coordinate SBML import, pathway graph construction,
    and visualization scene generation.

    Each stage delegates to its own independent component.
    """

    def __init__(
        self,
        import_service: SBMLImportService | None = None,
        visualization_service: PathwayVisualizationService | None = None,
    ) -> None:
        if import_service is not None and not isinstance(
            import_service,
            SBMLImportService,
        ):
            raise TypeError(
                "import_service must be an SBMLImportService instance."
            )

        if visualization_service is not None and not isinstance(
            visualization_service,
            PathwayVisualizationService,
        ):
            raise TypeError(
                "visualization_service must be a "
                "PathwayVisualizationService instance."
            )

        self._import_service = (
            import_service
            if import_service is not None
            else SBMLImportService()
        )

        self._visualization_service = (
            visualization_service
            if visualization_service is not None
            else PathwayVisualizationService()
        )

    @property
    def available_layouts(self) -> tuple[str, ...]:
        """Return the available pathway layout identifiers."""

        return self._visualization_service.available_layouts

    def visualize(
        self,
        source: str | bytes,
        layout_id: str = "hierarchical",
    ) -> PathwayScene:
        """
        Import an SBML document and generate its visualization scene.

        Args:
            source: SBML XML document as a string or bytes.
            layout_id: Registered pathway layout algorithm.

        Returns:
            A render-ready PathwayScene.

        Raises:
            TypeError: If the source is not a string or bytes.
            SBMLParseError: If the SBML document is invalid.
            SBMLConversionError: If domain conversion fails.
            LayoutRegistryError: If the layout is unavailable.
        """

        if not isinstance(source, (str, bytes)):
            raise TypeError(
                "SBML source must be a string or bytes."
            )

        if not isinstance(layout_id, str) or not layout_id.strip():
            raise ValueError(
                "layout_id must be a non-empty string."
            )

        pathway = self._import_service.import_pathway(source)

        pathway_graph = PathwayGraph.from_pathway(pathway)

        return self._visualization_service.create_scene(
            pathway_graph=pathway_graph,
            layout_id=layout_id,
        )
