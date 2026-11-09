
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways.metabolite import Metabolite
from aditi.domain.pathways.pathway import Pathway
from aditi.domain.pathways.reaction import Reaction


class GraphNodeType(Enum):
    """Identifies the biological entity represented by a graph node."""

    METABOLITE = "metabolite"
    REACTION = "reaction"


class GraphEdgeRole(Enum):
    """Identifies how a metabolite participates in a reaction."""

    REACTANT = "reactant"
    PRODUCT = "product"


@dataclass(frozen=True, slots=True)
class GraphNode:
    """
    Represents a biological entity as a graph node.

    The node references the original domain entity and reuses
    its internal identity.
    """

    entity: Metabolite | Reaction

    def __post_init__(self) -> None:
        if not isinstance(self.entity, (Metabolite, Reaction)):
            raise TypeError(
                "Graph nodes must reference Metabolite or Reaction instances."
            )

    @property
    def identity(self) -> EntityIdentity:
        """Return the identity of the represented biological entity."""
        return self.entity.identity

    @property
    def node_type(self) -> GraphNodeType:
        """Return the graph node category."""

        if isinstance(self.entity, Metabolite):
            return GraphNodeType.METABOLITE

        return GraphNodeType.REACTION


@dataclass(frozen=True, slots=True)
class GraphEdge:
    """
    Represents a directed connection between a metabolite and reaction.

    Reactant edges point from metabolite to reaction.
    Product edges point from reaction to metabolite.
    """

    source_identity: EntityIdentity
    target_identity: EntityIdentity
    role: GraphEdgeRole
    coefficient: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.source_identity, EntityIdentity):
            raise TypeError(
                "Graph edge source must be an EntityIdentity."
            )

        if not isinstance(self.target_identity, EntityIdentity):
            raise TypeError(
                "Graph edge target must be an EntityIdentity."
            )

        if not isinstance(self.role, GraphEdgeRole):
            raise TypeError(
                "Graph edge role must be a GraphEdgeRole."
            )

        if not isinstance(self.coefficient, Decimal):
            raise TypeError(
                "Graph edge coefficient must be a Decimal."
            )

        if not self.coefficient.is_finite():
            raise ValueError(
                "Graph edge coefficient must be finite."
            )

        if self.coefficient <= 0:
            raise ValueError(
                "Graph edge coefficient must be greater than zero."
            )


@dataclass(frozen=True, slots=True)
class PathwayGraph:
    """
    Computational graph representation of a biological pathway.

    The graph is bipartite:
    - Metabolite nodes represent biochemical substances.
    - Reaction nodes represent biochemical transformations.

    Directed edges preserve reactant and product relationships.
    """

    pathway_identity: EntityIdentity
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.pathway_identity, EntityIdentity):
            raise TypeError(
                "Pathway graph identity must be an EntityIdentity."
            )

        if not isinstance(self.nodes, tuple):
            raise TypeError(
                "Pathway graph nodes must be provided as a tuple."
            )

        if not isinstance(self.edges, tuple):
            raise TypeError(
                "Pathway graph edges must be provided as a tuple."
            )

        node_index: dict[EntityIdentity, GraphNode] = {}

        for node in self.nodes:
            if not isinstance(node, GraphNode):
                raise TypeError(
                    "All pathway graph nodes must be GraphNode instances."
                )

            if node.identity in node_index:
                raise ValueError(
                    "Pathway graph cannot contain duplicate nodes."
                )

            node_index[node.identity] = node

        seen_edges: set[
            tuple[EntityIdentity, EntityIdentity, GraphEdgeRole]
        ] = set()

        for edge in self.edges:
            if not isinstance(edge, GraphEdge):
                raise TypeError(
                    "All pathway graph edges must be GraphEdge instances."
                )

            source = node_index.get(edge.source_identity)
            target = node_index.get(edge.target_identity)

            if source is None or target is None:
                raise ValueError(
                    "Graph edge references a node that does not exist."
                )

            if edge.role is GraphEdgeRole.REACTANT:
                valid_direction = (
                    source.node_type is GraphNodeType.METABOLITE
                    and target.node_type is GraphNodeType.REACTION
                )

            else:
                valid_direction = (
                    source.node_type is GraphNodeType.REACTION
                    and target.node_type is GraphNodeType.METABOLITE
                )

            if not valid_direction:
                raise ValueError(
                    f"Invalid direction for {edge.role.value} graph edge."
                )

            edge_key = (
                edge.source_identity,
                edge.target_identity,
                edge.role,
            )

            if edge_key in seen_edges:
                raise ValueError(
                    "Pathway graph cannot contain duplicate edges."
                )

            seen_edges.add(edge_key)

    @classmethod
    def from_pathway(cls, pathway: Pathway) -> PathwayGraph:
        """
        Construct a directed bipartite graph from a biological pathway.

        Nodes and edges preserve the order of the pathway's reactions
        and their participant declarations.
        """

        if not isinstance(pathway, Pathway):
            raise TypeError(
                "Pathway graph construction requires a Pathway instance."
            )

        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        seen_nodes: set[EntityIdentity] = set()

        def add_node(entity: Metabolite | Reaction) -> None:
            if entity.identity in seen_nodes:
                return

            seen_nodes.add(entity.identity)
            nodes.append(GraphNode(entity=entity))

        for reaction in pathway.reactions:
            for participant in reaction.reactants:
                metabolite = participant.metabolite

                add_node(metabolite)
                add_node(reaction)

                edges.append(
                    GraphEdge(
                        source_identity=metabolite.identity,
                        target_identity=reaction.identity,
                        role=GraphEdgeRole.REACTANT,
                        coefficient=participant.coefficient,
                    )
                )

            for participant in reaction.products:
                metabolite = participant.metabolite

                add_node(reaction)
                add_node(metabolite)

                edges.append(
                    GraphEdge(
                        source_identity=reaction.identity,
                        target_identity=metabolite.identity,
                        role=GraphEdgeRole.PRODUCT,
                        coefficient=participant.coefficient,
                    )
                )

        return cls(
            pathway_identity=pathway.identity,
            nodes=tuple(nodes),
            edges=tuple(edges),
        )

    @property
    def metabolite_nodes(self) -> tuple[GraphNode, ...]:
        """Return all metabolite nodes."""
        return tuple(
            node
            for node in self.nodes
            if node.node_type is GraphNodeType.METABOLITE
        )

    @property
    def reaction_nodes(self) -> tuple[GraphNode, ...]:
        """Return all reaction nodes."""
        return tuple(
            node
            for node in self.nodes
            if node.node_type is GraphNodeType.REACTION
        )
