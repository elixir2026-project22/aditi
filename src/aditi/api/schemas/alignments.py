
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from aditi.domain.sequences.alignment import AlignmentResult
from aditi.domain.sequences.alignment.alignment_score import AlignmentScore


class AlignmentAPIModel(BaseModel):
    """Base configuration shared by alignment response models."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class AlignedSequenceSchema(AlignmentAPIModel):
    """API representation of one aligned biological sequence."""

    sequence_identity: UUID
    sequence_name: str = Field(min_length=1)
    residues: str = Field(min_length=1)
    position_mapping: tuple[int | None, ...]


class AlignmentScoreSchema(AlignmentAPIModel):
    """API representation of alignment scoring metadata."""

    score: float
    scoring_scheme: str

    gap_open_penalty: float
    gap_extension_penalty: float

    substitution_matrix: str | None
    match_score: float | None
    mismatch_score: float | None

    @classmethod
    def from_score(
        cls,
        score: AlignmentScore,
    ) -> AlignmentScoreSchema:
        """Convert an internal alignment score into an API schema."""

        if not isinstance(score, AlignmentScore):
            raise TypeError(
                "Alignment score schema requires an AlignmentScore."
            )

        return cls(
            score=score.score,
            scoring_scheme=score.scoring_scheme,
            gap_open_penalty=score.gap_open_penalty,
            gap_extension_penalty=score.gap_extension_penalty,
            substitution_matrix=score.substitution_matrix,
            match_score=score.match_score,
            mismatch_score=score.mismatch_score,
        )


class SequenceAlignmentResponse(AlignmentAPIModel):
    """Complete API representation of a pairwise alignment result."""

    alignment_type: str

    aligned_sequences: tuple[AlignedSequenceSchema, ...]

    alignment_length: int = Field(ge=1)
    sequence_count: int = Field(ge=2)

    score: AlignmentScoreSchema

    identical_positions: int = Field(ge=0)
    similar_positions: int | None = Field(default=None, ge=0)

    gap_count: int = Field(ge=0)
    gap_percentage: float = Field(ge=0, le=100)

    identity_percentage: float = Field(ge=0, le=100)
    similarity_percentage: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    @classmethod
    def from_result(
        cls,
        result: AlignmentResult,
        sequence_names: dict[UUID, str],
    ) -> SequenceAlignmentResponse:
        """Convert a domain alignment result into an API response."""

        if not isinstance(result, AlignmentResult):
            raise TypeError(
                "Alignment response requires an AlignmentResult."
            )

        aligned_sequences = tuple(
            AlignedSequenceSchema(
                sequence_identity=sequence.sequence_identity.value,
                sequence_name=sequence_names[
                    sequence.sequence_identity.value
                ],
                residues=sequence.residues,
                position_mapping=sequence.position_mapping,
            )
            for sequence in result.aligned_sequences
        )

        return cls(
            alignment_type=result.alignment_type.value,
            aligned_sequences=aligned_sequences,
            alignment_length=result.alignment_length,
            sequence_count=result.sequence_count,
            score=AlignmentScoreSchema.from_score(result.score),
            identical_positions=result.identical_positions,
            similar_positions=result.similar_positions,
            gap_count=result.gap_count,
            gap_percentage=result.gap_percentage,
            identity_percentage=result.identity_percentage,
            similarity_percentage=result.similarity_percentage,
        )
