
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from aditi.domain.sequences.alignment import AlignmentType
from aditi.domain.sequences.alphabet import SequenceAlphabet


class AlignmentRequestModel(BaseModel):
    """Base configuration shared by alignment request models."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class BiologicalSequenceRequest(AlignmentRequestModel):
    """Input definition for a biological sequence."""

    name: str = Field(min_length=1)
    residues: str = Field(min_length=1)
    alphabet: SequenceAlphabet
    description: str | None = None


class AlignmentScoringRequest(AlignmentRequestModel):
    """Configuration for simple or substitution-matrix scoring."""

    method: Literal["simple", "substitution_matrix"] = "simple"

    match_score: float = Field(default=2.0, allow_inf_nan=False)
    mismatch_score: float = Field(default=-1.0, allow_inf_nan=False)

    matrix_name: Literal["BLOSUM62"] | None = None

    @model_validator(mode="after")
    def validate_scoring_configuration(
        self,
    ) -> AlignmentScoringRequest:
        """Ensure the selected scoring method has valid parameters."""

        if self.method == "simple" and self.matrix_name is not None:
            raise ValueError(
                "A substitution matrix cannot be specified "
                "when using simple scoring."
            )

        if (
            self.method == "substitution_matrix"
            and self.matrix_name is None
        ):
            raise ValueError(
                "A substitution matrix name is required "
                "for substitution-matrix scoring."
            )

        return self


class AlignmentGapRequest(AlignmentRequestModel):
    """Configuration for linear or affine gap penalties."""

    model: Literal["linear", "affine"] = "linear"

    gap_penalty: float = Field(
        default=-2.0,
        le=0,
        allow_inf_nan=False,
    )

    gap_open_penalty: float = Field(
        default=-5.0,
        le=0,
        allow_inf_nan=False,
    )

    gap_extension_penalty: float = Field(
        default=-1.0,
        le=0,
        allow_inf_nan=False,
    )


class SequenceAlignmentRequest(AlignmentRequestModel):
    """Complete pairwise sequence-alignment request."""

    first_sequence: BiologicalSequenceRequest
    second_sequence: BiologicalSequenceRequest

    alignment_type: AlignmentType = AlignmentType.GLOBAL

    scoring: AlignmentScoringRequest = Field(
        default_factory=AlignmentScoringRequest
    )

    gap: AlignmentGapRequest = Field(
        default_factory=AlignmentGapRequest
    )

    @model_validator(mode="after")
    def validate_alignment_request(
        self,
    ) -> SequenceAlignmentRequest:
        """Validate compatibility between sequences and scoring."""

        if self.alignment_type is AlignmentType.MULTIPLE:
            raise ValueError(
                "Multiple sequence alignment is not supported "
                "by the current pairwise alignment service."
            )

        if self.first_sequence.alphabet is not self.second_sequence.alphabet:
            raise ValueError(
                "Both sequences must use the same biological alphabet."
            )

        if (
            self.scoring.method == "substitution_matrix"
            and self.first_sequence.alphabet is not SequenceAlphabet.PROTEIN
        ):
            raise ValueError(
                "BLOSUM62 scoring requires protein sequences."
            )

        return self
