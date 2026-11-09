
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import isfinite

from aditi.domain.entities.identity import EntityIdentity
from aditi.visualization.pathways.model import PathwayVisualization


@dataclass(frozen=True, slots=True)
class NodePosition:
    """Represents the two-dimensional position of a visual node."""

    identity: EntityIdentity
    x: float
    y: float

    def __post_init__(self) -> None:
        if not isinstance(self.identity, EntityIdentity):
            raise TypeError(
                "Node position identity must be an EntityIdentity."
            )

        for coordinate_name, coordinate in (
            ("x", self.x),
            ("y", self.y),
        ):
            if (
                isinstance(coordinate, bool)
                or not isinstance(coordinate, (int, float))
            ):
                raise TypeError(
                    f"Node position {coordinate_name} must be numeric."
                )

            if not isfinite(coordinate):
                raise ValueError(
                    f"Node position {coordinate_name} must be finite."
                )


@dataclass(frozen=True, slots=True)
class PathwayLayout:
    """
    Contains the calculated positions of pathway visualization nodes.

    This model does not depend on a rendering library or coordinate
    system used by a particular frontend.
    """

    pathway_identity: EntityIdentity
    positions: tuple[NodePosition, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.pathway_identity, EntityIdentity):
            raise TypeError(
                "Layout pathway identity must be an EntityIdentity."
            )

        if not isinstance(self.positions, tuple):
            raise TypeError(
                "Layout positions must be provided as a tuple."
            )

        seen_identities: set[EntityIdentity] = set()

        for position in self.positions:
            if not isinstance(position, NodePosition):
                raise TypeError(
                    "All layout positions must be NodePosition instances."
                )

            if position.identity in seen_identities:
                raise ValueError(
                    "A layout cannot contain duplicate node positions."
                )

            seen_identities.add(position.identity)

    def get_position(
        self,
        identity: EntityIdentity,
    ) -> NodePosition | None:
        """Retrieve the position associated with a node identity."""

        for position in self.positions:
            if position.identity == identity:
                return position

        return None


class PathwayLayoutAlgorithm(ABC):
    """Contract implemented by all pathway layout algorithms."""

    @abstractmethod
    def calculate(
        self,
        visualization: PathwayVisualization,
    ) -> PathwayLayout:
        """Calculate the positions of visualization nodes."""
        raise NotImplementedError
