
from aditi.domain.pathways.graph import PathwayGraph
from aditi.visualization.pathways.layouts import (
    ForceDirectedLayout,
    HierarchicalLayout,
    PathwayLayoutRegistry,
)
from aditi.visualization.pathways.model import PathwayVisualization
from aditi.visualization.pathways.scene import PathwayScene


class PathwayVisualizationService:
    """
    Coordinates pathway visualization model creation, layout
    calculation, and scene construction.

    The service hides the individual visualization steps from
    application-level callers while allowing layout algorithms
    to be selected through the layout registry.
    """

    def __init__(
        self,
        layout_registry: PathwayLayoutRegistry | None = None,
    ) -> None:
        if layout_registry is not None and not isinstance(
            layout_registry,
            PathwayLayoutRegistry,
        ):
            raise TypeError(
                "Layout registry must be a PathwayLayoutRegistry."
            )

        self._layout_registry = (
            layout_registry
            if layout_registry is not None
            else self.create_default_registry()
        )

    @staticmethod
    def create_default_registry() -> PathwayLayoutRegistry:
        """Create a registry containing the built-in layouts."""

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

    @property
    def available_layouts(self) -> tuple[str, ...]:
        """Return the identifiers of available layout algorithms."""

        return self._layout_registry.available_layouts

    def create_scene(
        self,
        pathway_graph: PathwayGraph,
        layout_id: str = "hierarchical",
    ) -> PathwayScene:
        """
        Build a complete visualization scene from a pathway graph.

        The selected layout algorithm determines node positions.
        The resulting scene combines those positions with the
        renderer-independent visualization model.
        """

        if not isinstance(pathway_graph, PathwayGraph):
            raise TypeError(
                "Pathway visualization requires a PathwayGraph."
            )

        visualization = PathwayVisualization.from_graph(
            pathway_graph
        )

        algorithm = self._layout_registry.resolve(
            layout_id
        )

        layout = algorithm.calculate(
            visualization
        )

        return PathwayScene.from_models(
            visualization,
            layout,
        )
