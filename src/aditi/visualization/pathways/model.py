
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways.graph import (
    GraphEdgeRole,
    GraphNodeType,
    PathwayGraph,
)


@dataclass(frozen=True, slots=True)
class PathwayVisualNode:
    """Renderer-independent representation of a pathway graph node."""

    identity: EntityIdentity
    node_type: GraphNodeType
    label: str

    def __post_init__(self) -> None:
        if not isinstance(self.identity, EntityIdentity):
            raise TypeError(
                "Visual node identity must be an EntityIdentity."
            )

        if not isinstance(self.node_type, GraphNodeType):
            raise TypeError(
                "Visual node type must be a GraphNodeType."
            )

        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError(
                "Visual node label must be a non-empty string."
            )

        if self.label != self.label.strip():
            raise ValueError(
                "Visual node label cannot contain leading or trailing whitespace."
            )


@dataclass(frozen=True, slots=True)
class PathwayVisualEdge:
    """Renderer-independent representation of a pathway graph edge."""

    source_identity: EntityIdentity
    target_identity: EntityIdentity
    role: GraphEdgeRole
    coefficient: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.source_identity, EntityIdentity):
            raise TypeError(
                "Visual edge source must be an EntityIdentity."
            )

        if not isinstance(self.target_identity, EntityIdentity):
            raise TypeError(
                "Visual edge target must be an EntityIdentity."
            )

        if not isinstance(self.role, GraphEdgeRole):
            raise TypeError(
                "Visual edge role must be a GraphEdgeRole."
            )

        if not isinstance(self.coefficient, Decimal):
            raise TypeError(
                "Visual edge coefficient must be a Decimal."
            )

        if not self.coefficient.is_finite():
            raise ValueError(
                "Visual edge coefficient must be finite."
            )

        if self.coefficient <= 0:
            raise ValueError(
                "Visual edge coefficient must be greater than zero."
            )


@dataclass(frozen=True, slots=True)
class PathwayVisualization:
    """
    Renderer-independent visualization model of a biological pathway.

    The model contains visual nodes and edges without assigning
    screen positions or depending on a rendering technology.
    """

    pathway_identity: EntityIdentity
    nodes: tuple[PathwayVisualNode, ...]
    edges: tuple[PathwayVisualEdge, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.pathway_identity, EntityIdentity):
            raise TypeError(
                "Visualization pathway identity must be an EntityIdentity."
            )

        if not isinstance(self.nodes, tuple):
            raise TypeError(
                "Visualization nodes must be provided as a tuple."
            )

        if not isinstance(self.edges, tuple):
            raise TypeError(
                "Visualization edges must be provided as a tuple."
            )

        node_index: dict[EntityIdentity, PathwayVisualNode] = {}

        for node in self.nodes:
            if not isinstance(node, PathwayVisualNode):
                raise TypeError(
                    "All visualization nodes must be PathwayVisualNode instances."
                )

            if node.identity in node_index:
                raise ValueError(
                    "Visualization cannot contain duplicate nodes."
                )

            node_index[node.identity] = node

        seen_edges: set[
            tuple[EntityIdentity, EntityIdentity, GraphEdgeRole]
        ] = set()

        for edge in self.edges:
            if not isinstance(edge, PathwayVisualEdge):
                raise TypeError(
                    "All visualization edges must be PathwayVisualEdge instances."
                )

            source = node_index.get(edge.source_identity)
            target = node_index.get(edge.target_identity)

            if source is None or target is None:
                raise ValueError(
                    "Visualization edge references a node that does not exist."
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
                    f"Invalid direction for {edge.role.value} visual edge."
                )

            edge_key = (
                edge.source_identity,
                edge.target_identity,
                edge.role,
            )

            if edge_key in seen_edges:
                raise ValueError(
                    "Visualization cannot contain duplicate edges."
                )

            seen_edges.add(edge_key)

    @classmethod
    def from_graph(
        cls,
        graph: PathwayGraph,
    ) -> PathwayVisualization:
        """Convert a biological pathway graph into a visualization model."""

        if not isinstance(graph, PathwayGraph):
            raise TypeError(
                "Visualization construction requires a PathwayGraph instance."
            )

        nodes = tuple(
            PathwayVisualNode(
                identity=node.identity,
                node_type=node.node_type,
                label=node.entity.name,
            )
            for node in graph.nodes
        )

        edges = tuple(
            PathwayVisualEdge(
                source_identity=edge.source_identity,
                target_identity=edge.target_identity,
                role=edge.role,
                coefficient=edge.coefficient,
            )
            for edge in graph.edges
        )

        return cls(
            pathway_identity=graph.pathway_identity,
            nodes=nodes,
            edges=edges,
        )

    @property
    def metabolite_nodes(self) -> tuple[PathwayVisualNode, ...]:
        """Return all visual metabolite nodes."""

        return tuple(
            node
            for node in self.nodes
            if node.node_type is GraphNodeType.METABOLITE
        )

    @property
    def reaction_nodes(self) -> tuple[PathwayVisualNode, ...]:
        """Return all visual reaction nodes."""

        return tuple(
            node
            for node in self.nodes
            if node.node_type is GraphNodeType.REACTION
        )
