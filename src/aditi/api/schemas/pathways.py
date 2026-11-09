
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from aditi.domain.pathways.graph import (
    GraphEdgeRole,
    GraphNodeType,
)
from aditi.visualization.pathways.scene import PathwayScene


class PathwayAPIModel(BaseModel):
    """Base configuration shared by pathway API models."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class PathwaySceneNodeSchema(PathwayAPIModel):
    """API representation of a positioned pathway node."""

    identity: UUID
    node_type: GraphNodeType
    label: str = Field(min_length=1)
    x: float
    y: float


class PathwaySceneEdgeSchema(PathwayAPIModel):
    """API representation of a directed pathway edge."""

    source_identity: UUID
    target_identity: UUID
    role: GraphEdgeRole
    coefficient: Decimal = Field(gt=0)


class PathwaySceneBoundsSchema(PathwayAPIModel):
    """API representation of pathway scene boundaries."""

    min_x: float
    min_y: float
    max_x: float
    max_y: float
    width: float = Field(ge=0)
    height: float = Field(ge=0)


class PathwaySceneResponse(PathwayAPIModel):
    """
    Complete API response representation of a pathway scene.

    This schema is independent of the renderer and can be consumed
    by different clients, including the future React application.
    """

    pathway_identity: UUID
    nodes: tuple[PathwaySceneNodeSchema, ...]
    edges: tuple[PathwaySceneEdgeSchema, ...]
    bounds: PathwaySceneBoundsSchema | None

    @classmethod
    def from_scene(
        cls,
        scene: PathwayScene,
    ) -> PathwaySceneResponse:
        """Convert an internal pathway scene into an API response."""

        if not isinstance(scene, PathwayScene):
            raise TypeError(
                "Pathway API response requires a PathwayScene."
            )

        nodes = tuple(
            PathwaySceneNodeSchema(
                identity=node.identity.value,
                node_type=node.node_type,
                label=node.label,
                x=node.x,
                y=node.y,
            )
            for node in scene.nodes
        )

        edges = tuple(
            PathwaySceneEdgeSchema(
                source_identity=edge.source_identity.value,
                target_identity=edge.target_identity.value,
                role=edge.role,
                coefficient=edge.coefficient,
            )
            for edge in scene.edges
        )

        scene_bounds = scene.bounds

        bounds = (
            PathwaySceneBoundsSchema(
                min_x=scene_bounds.min_x,
                min_y=scene_bounds.min_y,
                max_x=scene_bounds.max_x,
                max_y=scene_bounds.max_y,
                width=scene_bounds.width,
                height=scene_bounds.height,
            )
            if scene_bounds is not None
            else None
        )

        return cls(
            pathway_identity=scene.pathway_identity.value,
            nodes=nodes,
            edges=edges,
            bounds=bounds,
        )
