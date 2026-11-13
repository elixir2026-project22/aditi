
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways.graph import (
    GraphEdgeRole,
    GraphNodeType,
)
from aditi.visualization.pathways.layouts.base import (
    NodePosition,
    PathwayLayout,
)
from aditi.visualization.pathways.model import (
    PathwayVisualEdge,
    PathwayVisualization,
    PathwayVisualNode,
)


@dataclass(frozen=True, slots=True)
class SceneBounds:
    """Describes the rectangular bounds occupied by a pathway scene."""

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def __post_init__(self) -> None:
        for name, value in (
            ("min_x", self.min_x),
            ("min_y", self.min_y),
            ("max_x", self.max_x),
            ("max_y", self.max_y),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(
                    f"Scene bound '{name}' must be numeric."
                )

            if not isfinite(value):
                raise ValueError(
                    f"Scene bound '{name}' must be finite."
                )

        if self.min_x > self.max_x:
            raise ValueError(
                "Scene minimum X cannot exceed maximum X."
            )

        if self.min_y > self.max_y:
            raise ValueError(
                "Scene minimum Y cannot exceed maximum Y."
            )

    @property
    def width(self) -> float:
        """Return the horizontal extent of the scene."""
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        """Return the vertical extent of the scene."""
        return self.max_y - self.min_y


@dataclass(frozen=True, slots=True)
class PathwaySceneNode:
    """
    Combines a visual pathway node with its calculated position.

    The original visual node remains available so that biological
    identity, category, and display information are preserved.
    """

    visual_node: PathwayVisualNode
    position: NodePosition

    def __post_init__(self) -> None:
        if not isinstance(self.visual_node, PathwayVisualNode):
            raise TypeError(
                "Scene visual node must be a PathwayVisualNode."
            )

        if not isinstance(self.position, NodePosition):
            raise TypeError(
                "Scene node position must be a NodePosition."
            )

        if self.visual_node.identity != self.position.identity:
            raise ValueError(
                "Scene node and position identities must match."
            )

    @property
    def identity(self) -> EntityIdentity:
        """Return the biological identity of the visual node."""
        return self.visual_node.identity

    @property
    def node_type(self) -> GraphNodeType:
        """Return the biological category of the visual node."""
        return self.visual_node.node_type

    @property
    def label(self) -> str:
        """Return the display label of the visual node."""
        return self.visual_node.label

    @property
    def x(self) -> float:
        """Return the horizontal scene coordinate."""
        return self.position.x

    @property
    def y(self) -> float:
        """Return the vertical scene coordinate."""
        return self.position.y


@dataclass(frozen=True, slots=True)
class PathwayScene:
    """
    Renderer-independent scene containing positioned pathway elements.

    A scene combines visual nodes, calculated positions, and directed
    edges into one structure suitable for renderer adapters.
    """

    pathway_identity: EntityIdentity
    nodes: tuple[PathwaySceneNode, ...]
    edges: tuple[PathwayVisualEdge, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.pathway_identity, EntityIdentity):
            raise TypeError(
                "Scene pathway identity must be an EntityIdentity."
            )

        if not isinstance(self.nodes, tuple):
            raise TypeError(
                "Scene nodes must be provided as a tuple."
            )

        if not isinstance(self.edges, tuple):
            raise TypeError(
                "Scene edges must be provided as a tuple."
            )

        node_index: dict[EntityIdentity, PathwaySceneNode] = {}

        for node in self.nodes:
            if not isinstance(node, PathwaySceneNode):
                raise TypeError(
                    "All scene nodes must be PathwaySceneNode instances."
                )

            if node.identity in node_index:
                raise ValueError(
                    "A pathway scene cannot contain duplicate nodes."
                )

            node_index[node.identity] = node

        seen_edges: set[
            tuple[EntityIdentity, EntityIdentity, GraphEdgeRole]
        ] = set()

        for edge in self.edges:
            if not isinstance(edge, PathwayVisualEdge):
                raise TypeError(
                    "All scene edges must be PathwayVisualEdge instances."
                )

            source = node_index.get(edge.source_identity)
            target = node_index.get(edge.target_identity)

            if source is None or target is None:
                raise ValueError(
                    "Scene edge references a node that does not exist."
                )

            if edge.role in (
                GraphEdgeRole.REACTANT,
                GraphEdgeRole.MODIFIER,
            ):
                valid_direction = (
                    source.node_type is GraphNodeType.METABOLITE
                    and target.node_type is GraphNodeType.REACTION
                )

            elif edge.role is GraphEdgeRole.PRODUCT:
                valid_direction = (
                    source.node_type is GraphNodeType.REACTION
                    and target.node_type is GraphNodeType.METABOLITE
                )

            else:
                valid_direction = False

            if not valid_direction:
                raise ValueError(
                    f"Invalid direction for {edge.role.value} scene edge."
                )

            edge_key = (
                edge.source_identity,
                edge.target_identity,
                edge.role,
            )

            if edge_key in seen_edges:
                raise ValueError(
                    "A pathway scene cannot contain duplicate edges."
                )

            seen_edges.add(edge_key)

    @classmethod
    def from_models(
        cls,
        visualization: PathwayVisualization,
        layout: PathwayLayout,
    ) -> PathwayScene:
        """
        Combine a pathway visualization and layout into a scene.

        Every visual node must have exactly one corresponding position.
        """

        if not isinstance(visualization, PathwayVisualization):
            raise TypeError(
                "Scene construction requires a PathwayVisualization."
            )

        if not isinstance(layout, PathwayLayout):
            raise TypeError(
                "Scene construction requires a PathwayLayout."
            )

        if visualization.pathway_identity != layout.pathway_identity:
            raise ValueError(
                "Visualization and layout must belong to the same pathway."
            )

        visual_identities = {
            node.identity
            for node in visualization.nodes
        }

        position_index = {
            position.identity: position
            for position in layout.positions
        }

        if visual_identities != set(position_index):
            raise ValueError(
                "Layout positions must match the visualization nodes exactly."
            )

        scene_nodes = tuple(
            PathwaySceneNode(
                visual_node=node,
                position=position_index[node.identity],
            )
            for node in visualization.nodes
        )

        return cls(
            pathway_identity=visualization.pathway_identity,
            nodes=scene_nodes,
            edges=visualization.edges,
        )

    def get_node(
        self,
        identity: EntityIdentity,
    ) -> PathwaySceneNode | None:
        """Retrieve a scene node by biological identity."""

        for node in self.nodes:
            if node.identity == identity:
                return node

        return None

    @property
    def metabolite_nodes(self) -> tuple[PathwaySceneNode, ...]:
        """Return all positioned metabolite nodes."""

        return tuple(
            node
            for node in self.nodes
            if node.node_type is GraphNodeType.METABOLITE
        )

    @property
    def reaction_nodes(self) -> tuple[PathwaySceneNode, ...]:
        """Return all positioned reaction nodes."""

        return tuple(
            node
            for node in self.nodes
            if node.node_type is GraphNodeType.REACTION
        )

    @property
    def bounds(self) -> SceneBounds | None:
        """Return the bounding rectangle of all scene nodes."""

        if not self.nodes:
            return None

        x_coordinates = [
            node.x
            for node in self.nodes
        ]

        y_coordinates = [
            node.y
            for node in self.nodes
        ]

        return SceneBounds(
            min_x=min(x_coordinates),
            min_y=min(y_coordinates),
            max_x=max(x_coordinates),
            max_y=max(y_coordinates),
        )
