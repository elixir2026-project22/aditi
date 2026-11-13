
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from aditi.api.alignment_service import AlignmentAPIService
from aditi.api.pathway_builder import PathwayGraphBuilder
from aditi.api.pathway_service import PathwayAPIService
from aditi.api.schemas.alignment_requests import SequenceAlignmentRequest
from aditi.api.schemas.alignments import SequenceAlignmentResponse
from aditi.api.schemas.pathway_requests import PathwayDefinitionRequest
from aditi.api.schemas.pathways import PathwaySceneResponse
from aditi.data.normalization.sbml import SBMLConversionError
from aditi.data.parsers.sbml import SBMLParseError
from aditi.modules.pathways.sbml_visualization import (
    SBMLVisualizationWorkflow,
)
from aditi.visualization.pathways.layouts.registry import (
    LayoutRegistryError,
)


def create_app(
    pathway_builder: PathwayGraphBuilder | None = None,
    pathway_service: PathwayAPIService | None = None,
    sbml_workflow: SBMLVisualizationWorkflow | None = None,
    alignment_service: AlignmentAPIService | None = None,
) -> FastAPI:
    """Create the Aditi API application with injectable services."""

    builder = (
        pathway_builder
        if pathway_builder is not None
        else PathwayGraphBuilder()
    )

    service = (
        pathway_service
        if pathway_service is not None
        else PathwayAPIService()
    )

    workflow = (
        sbml_workflow
        if sbml_workflow is not None
        else SBMLVisualizationWorkflow()
    )

    sequence_alignment_service = (
        alignment_service
        if alignment_service is not None
        else AlignmentAPIService()
    )

    app = FastAPI(
        title="Aditi API",
        description="Biological pathway and molecular visualization API.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Accept"],
    )

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        return {
            "application": "Aditi",
            "status": "ok",
        }

    @app.get("/api/v1/pathways/layouts")
    def pathway_layouts() -> dict[str, list[str]]:
        return {"layouts": list(service.available_layouts)}

    @app.post(
        "/api/v1/pathways/visualize",
        response_model=PathwaySceneResponse,
    )
    def visualize_pathway(
        definition: PathwayDefinitionRequest,
        layout_id: str = "hierarchical",
    ) -> PathwaySceneResponse:
        try:
            graph = builder.build(definition)

            return service.create_visualization(
                pathway_graph=graph,
                layout_id=layout_id,
            )

        except LayoutRegistryError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

    @app.post(
        "/api/v1/pathways/import/sbml",
        response_model=PathwaySceneResponse,
    )
    async def import_sbml(
        request: Request,
        layout_id: str = "hierarchical",
    ) -> PathwaySceneResponse:
        """Import an SBML XML document and return its visualization scene."""

        content_type = request.headers.get(
            "content-type",
            "",
        ).split(";", maxsplit=1)[0].strip().lower()

        supported_content_types = {
            "application/sbml+xml",
            "application/xml",
            "text/xml",
        }

        if content_type not in supported_content_types:
            raise HTTPException(
                status_code=415,
                detail="Unsupported SBML content type.",
            )

        source = await request.body()

        if not source:
            raise HTTPException(
                status_code=422,
                detail="The SBML request body cannot be empty.",
            )

        if not layout_id.strip():
            raise HTTPException(
                status_code=422,
                detail="layout_id must be a non-empty string.",
            )

        try:
            scene = workflow.visualize(
                source=source,
                layout_id=layout_id,
            )

            return PathwaySceneResponse.from_scene(scene)

        except (SBMLParseError, SBMLConversionError) as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        except LayoutRegistryError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

    @app.post(
        "/api/v1/alignments/pairwise",
        response_model=SequenceAlignmentResponse,
    )
    def align_sequences(
        alignment_request: SequenceAlignmentRequest,
    ) -> SequenceAlignmentResponse:
        """Perform global or local pairwise biological sequence alignment."""

        try:
            return sequence_alignment_service.align(
                alignment_request,
            )

        except (ValueError, KeyError) as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

    return app


app = create_app()
