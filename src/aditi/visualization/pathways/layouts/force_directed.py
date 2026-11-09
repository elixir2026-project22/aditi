
from __future__ import annotations

from math import cos, isfinite, pi, sin, sqrt

from aditi.domain.entities.identity import EntityIdentity
from aditi.visualization.pathways.layouts.base import (
    NodePosition,
    PathwayLayout,
    PathwayLayoutAlgorithm,
)
from aditi.visualization.pathways.model import PathwayVisualization


class ForceDirectedLayout(PathwayLayoutAlgorithm):
    """
    Calculates pathway positions using a Fruchterman-Reingold-style layout.

    Connected nodes attract each other while all nodes repel each other.
    A deterministic circular initialization and fixed iteration schedule
    ensure repeatable results for the same input and configuration.

    Repulsion is calculated between every pair of nodes, giving this
    implementation O(V² + E) work per iteration.
    """

    def __init__(
        self,
        width: float = 1000.0,
        height: float = 800.0,
        iterations: int = 100,
        gravity: float = 0.05,
    ) -> None:
        self._validate_dimension(width, "Width")
        self._validate_dimension(height, "Height")
        self._validate_iterations(iterations)
        self._validate_gravity(gravity)

        self.width = float(width)
        self.height = float(height)
        self.iterations = iterations
        self.gravity = gravity

    @staticmethod
    def _validate_dimension(value: float, label: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{label} must be numeric.")

        if not isfinite(value) or value <= 0:
            raise ValueError(
                f"{label} must be finite and greater than zero."
            )

    @staticmethod
    def _validate_iterations(value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("Iterations must be an integer.")

        if value <= 0:
            raise ValueError("Iterations must be greater than zero.")

    @staticmethod
    def _validate_gravity(value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Gravity must be numeric.")

        if not isfinite(value) or value < 0:
            raise ValueError(
                "Gravity must be finite and non-negative."
            )

    def _initialize_positions(
        self,
        node_ids: tuple[EntityIdentity, ...],
    ) -> dict[EntityIdentity, tuple[float, float]]:
        """Place nodes deterministically around an initial circle."""

        count = len(node_ids)
        radius = min(self.width, self.height) * 0.35

        positions: dict[EntityIdentity, tuple[float, float]] = {}

        for index, identity in enumerate(node_ids):
            angle = (2.0 * pi * index) / count

            positions[identity] = (
                radius * cos(angle),
                radius * sin(angle),
            )

        return positions

    @staticmethod
    def _calculate_repulsion(
        positions: dict[EntityIdentity, tuple[float, float]],
        node_ids: tuple[EntityIdentity, ...],
        optimal_distance: float,
        displacement: dict[EntityIdentity, list[float]],
    ) -> None:
        """Apply pairwise repulsive forces between all nodes."""

        optimal_distance_squared = optimal_distance**2

        for index, first_id in enumerate(node_ids):
            first_x, first_y = positions[first_id]

            for second_id in node_ids[index + 1:]:
                second_x, second_y = positions[second_id]

                delta_x = first_x - second_x
                delta_y = first_y - second_y

                distance_squared = (
                    delta_x**2 + delta_y**2
                )

                if distance_squared < 1e-12:
                    delta_x = 1e-6
                    delta_y = 0.0
                    distance_squared = delta_x**2

                force_x = (
                    delta_x
                    * optimal_distance_squared
                    / distance_squared
                )

                force_y = (
                    delta_y
                    * optimal_distance_squared
                    / distance_squared
                )

                displacement[first_id][0] += force_x
                displacement[first_id][1] += force_y

                displacement[second_id][0] -= force_x
                displacement[second_id][1] -= force_y

    @staticmethod
    def _calculate_attraction(
        visualization: PathwayVisualization,
        positions: dict[EntityIdentity, tuple[float, float]],
        optimal_distance: float,
        displacement: dict[EntityIdentity, list[float]],
    ) -> None:
        """Apply attractive forces along pathway edges."""

        for edge in visualization.edges:
            source_x, source_y = positions[edge.source_identity]
            target_x, target_y = positions[edge.target_identity]

            delta_x = source_x - target_x
            delta_y = source_y - target_y

            distance = sqrt(
                delta_x**2 + delta_y**2
            )

            if distance < 1e-12:
                continue

            force_scale = distance / optimal_distance

            force_x = delta_x * force_scale
            force_y = delta_y * force_scale

            displacement[edge.source_identity][0] -= force_x
            displacement[edge.source_identity][1] -= force_y

            displacement[edge.target_identity][0] += force_x
            displacement[edge.target_identity][1] += force_y

    def calculate(
        self,
        visualization: PathwayVisualization,
    ) -> PathwayLayout:
        """Calculate force-directed positions for a pathway."""

        if not isinstance(visualization, PathwayVisualization):
            raise TypeError(
                "Force-directed layout requires a PathwayVisualization."
            )

        node_ids = tuple(
            node.identity
            for node in visualization.nodes
        )

        if not node_ids:
            return PathwayLayout(
                pathway_identity=visualization.pathway_identity,
                positions=(),
            )

        if len(node_ids) == 1:
            return PathwayLayout(
                pathway_identity=visualization.pathway_identity,
                positions=(
                    NodePosition(
                        identity=node_ids[0],
                        x=0.0,
                        y=0.0,
                    ),
                ),
            )

        positions = self._initialize_positions(node_ids)

        optimal_distance = sqrt(
            (self.width * self.height) / len(node_ids)
        )

        temperature = min(self.width, self.height) * 0.1

        for iteration in range(self.iterations):
            displacement = {
                identity: [0.0, 0.0]
                for identity in node_ids
            }

            self._calculate_repulsion(
                positions,
                node_ids,
                optimal_distance,
                displacement,
            )

            self._calculate_attraction(
                visualization,
                positions,
                optimal_distance,
                displacement,
            )

            for identity in node_ids:
                x, y = positions[identity]
                force_x, force_y = displacement[identity]

                # Apply a weak gravitational force toward the center.
                force_x -= x * self.gravity
                force_y -= y * self.gravity

                force_length = sqrt(
                    force_x**2 + force_y**2
                )

                if force_length < 1e-12:
                    continue

                movement = min(
                    force_length,
                    temperature,
                )

                x += (force_x / force_length) * movement
                y += (force_y / force_length) * movement

                # Keep all nodes inside the configured scene dimensions.
                x = max(
                    -self.width / 2,
                    min(self.width / 2, x),
                )

                y = max(
                    -self.height / 2,
                    min(self.height / 2, y),
                )

                positions[identity] = (x, y)

            temperature *= 1.0 - (
                iteration + 1
            ) / self.iterations

        return PathwayLayout(
            pathway_identity=visualization.pathway_identity,
            positions=tuple(
                NodePosition(
                    identity=identity,
                    x=positions[identity][0],
                    y=positions[identity][1],
                )
                for identity in node_ids
            ),
        )
