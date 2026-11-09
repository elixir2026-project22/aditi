
from __future__ import annotations

from collections import deque
from math import isfinite

from aditi.domain.entities.identity import EntityIdentity
from aditi.visualization.pathways.layouts.base import (
    NodePosition,
    PathwayLayout,
    PathwayLayoutAlgorithm,
)
from aditi.visualization.pathways.model import PathwayVisualization


class HierarchicalLayout(PathwayLayoutAlgorithm):
    """
    Calculates a left-to-right hierarchical pathway layout.

    Strongly connected components are assigned to the same layer.
    The resulting component graph is a DAG, allowing deterministic
    topological layer assignment.
    """

    def __init__(
        self,
        horizontal_spacing: float = 240.0,
        vertical_spacing: float = 120.0,
    ) -> None:
        self._validate_spacing(
            horizontal_spacing,
            "Horizontal spacing",
        )

        self._validate_spacing(
            vertical_spacing,
            "Vertical spacing",
        )

        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing

    @staticmethod
    def _validate_spacing(
        value: float,
        label: str,
    ) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            raise TypeError(f"{label} must be numeric.")

        if not isfinite(value) or value <= 0:
            raise ValueError(
                f"{label} must be finite and greater than zero."
            )

    @staticmethod
    def _build_adjacency(
        visualization: PathwayVisualization,
    ) -> tuple[
        tuple[EntityIdentity, ...],
        dict[EntityIdentity, list[EntityIdentity]],
        dict[EntityIdentity, list[EntityIdentity]],
    ]:
        """Build forward and reverse adjacency lists."""

        node_ids = tuple(
            node.identity
            for node in visualization.nodes
        )

        adjacency = {
            identity: []
            for identity in node_ids
        }

        reverse_adjacency = {
            identity: []
            for identity in node_ids
        }

        for edge in visualization.edges:
            adjacency[edge.source_identity].append(
                edge.target_identity
            )

            reverse_adjacency[edge.target_identity].append(
                edge.source_identity
            )

        return (
            node_ids,
            adjacency,
            reverse_adjacency,
        )

    @staticmethod
    def _find_strongly_connected_components(
        node_ids: tuple[EntityIdentity, ...],
        adjacency: dict[
            EntityIdentity,
            list[EntityIdentity],
        ],
        reverse_adjacency: dict[
            EntityIdentity,
            list[EntityIdentity],
        ],
    ) -> tuple[tuple[EntityIdentity, ...], ...]:
        """Find strongly connected components using Kosaraju's algorithm."""

        visited: set[EntityIdentity] = set()
        finish_order: list[EntityIdentity] = []

        # First pass: calculate DFS finishing order.
        for start in node_ids:
            if start in visited:
                continue

            visited.add(start)

            stack = [
                (start, iter(adjacency[start]))
            ]

            while stack:
                current, neighbors = stack[-1]

                try:
                    neighbor = next(neighbors)

                except StopIteration:
                    finish_order.append(current)
                    stack.pop()
                    continue

                if neighbor in visited:
                    continue

                visited.add(neighbor)

                stack.append(
                    (
                        neighbor,
                        iter(adjacency[neighbor]),
                    )
                )

        # Second pass: traverse the reversed graph.
        assigned: set[EntityIdentity] = set()
        components: list[tuple[EntityIdentity, ...]] = []

        for start in reversed(finish_order):
            if start in assigned:
                continue

            assigned.add(start)

            component: list[EntityIdentity] = []
            stack = [start]

            while stack:
                current = stack.pop()
                component.append(current)

                for neighbor in reversed(
                    reverse_adjacency[current]
                ):
                    if neighbor in assigned:
                        continue

                    assigned.add(neighbor)
                    stack.append(neighbor)

            components.append(tuple(component))

        return tuple(components)

    @staticmethod
    def _build_component_layers(
        node_ids: tuple[EntityIdentity, ...],
        adjacency: dict[
            EntityIdentity,
            list[EntityIdentity],
        ],
        components: tuple[
            tuple[EntityIdentity, ...],
            ...,
        ],
    ) -> dict[EntityIdentity, int]:
        """Assign hierarchical layers to strongly connected components."""

        component_index: dict[EntityIdentity, int] = {}

        for index, component in enumerate(components):
            for identity in component:
                component_index[identity] = index

        component_edges = [
            set()
            for _ in components
        ]

        indegree = [
            0
            for _ in components
        ]

        for source in node_ids:
            source_component = component_index[source]

            for target in adjacency[source]:
                target_component = component_index[target]

                if source_component == target_component:
                    continue

                if target_component in component_edges[source_component]:
                    continue

                component_edges[source_component].add(
                    target_component
                )

                indegree[target_component] += 1

        # Components with no incoming edges begin at layer zero.
        queue = deque(
            index
            for index, degree in enumerate(indegree)
            if degree == 0
        )

        component_layers = [
            0
            for _ in components
        ]

        processed = 0

        while queue:
            current = queue.popleft()
            processed += 1

            for target in sorted(component_edges[current]):
                component_layers[target] = max(
                    component_layers[target],
                    component_layers[current] + 1,
                )

                indegree[target] -= 1

                if indegree[target] == 0:
                    queue.append(target)

        if processed != len(components):
            raise RuntimeError(
                "Component graph unexpectedly contains a cycle."
            )

        return {
            identity: component_layers[component_index[identity]]
            for identity in node_ids
        }

    def calculate(
        self,
        visualization: PathwayVisualization,
    ) -> PathwayLayout:
        """Calculate a deterministic hierarchical pathway layout."""

        if not isinstance(visualization, PathwayVisualization):
            raise TypeError(
                "Hierarchical layout requires a PathwayVisualization."
            )

        if not visualization.nodes:
            return PathwayLayout(
                pathway_identity=visualization.pathway_identity,
                positions=(),
            )

        (
            node_ids,
            adjacency,
            reverse_adjacency,
        ) = self._build_adjacency(visualization)

        components = self._find_strongly_connected_components(
            node_ids,
            adjacency,
            reverse_adjacency,
        )

        layers = self._build_component_layers(
            node_ids,
            adjacency,
            components,
        )

        # Preserve the original visualization node order within each layer.
        layer_nodes: dict[int, list[EntityIdentity]] = {}

        for identity in node_ids:
            layer = layers[identity]

            layer_nodes.setdefault(
                layer,
                [],
            ).append(identity)

        position_index: dict[
            EntityIdentity,
            NodePosition,
        ] = {}

        for layer, identities in layer_nodes.items():
            node_count = len(identities)

            for index, identity in enumerate(identities):
                x = layer * self.horizontal_spacing

                y = (
                    index - (node_count - 1) / 2
                ) * self.vertical_spacing

                position_index[identity] = NodePosition(
                    identity=identity,
                    x=x,
                    y=y,
                )

        positions = tuple(
            position_index[identity]
            for identity in node_ids
        )

        return PathwayLayout(
            pathway_identity=visualization.pathway_identity,
            positions=positions,
        )
