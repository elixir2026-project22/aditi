
from __future__ import annotations

from aditi.api.schemas.alignment_requests import SequenceAlignmentRequest
from aditi.api.schemas.alignments import SequenceAlignmentResponse
from aditi.domain.sequences import BiologicalSequence
from aditi.modules.sequence_alignment import AlignmentService
from aditi.modules.sequence_alignment.scoring import (
    AffineGapPenalty,
    BLOSUM62,
    LinearGapPenalty,
    SimpleScoringScheme,
    SubstitutionScoringScheme,
)


class AlignmentAPIService:
    """
    Application-facing service for pairwise sequence alignment requests.

    Converts validated API requests into domain sequences and scoring
    configurations, delegates computation to AlignmentService, and
    converts the result into an API response.

    This service does not depend on FastAPI or HTTP request objects.
    """

    def __init__(
        self,
        alignment_service: AlignmentService | None = None,
    ) -> None:
        if (
            alignment_service is not None
            and not isinstance(alignment_service, AlignmentService)
        ):
            raise TypeError(
                "Alignment service must be an AlignmentService."
            )

        self._alignment_service = (
            alignment_service
            if alignment_service is not None
            else AlignmentService()
        )

    def align(
        self,
        request: SequenceAlignmentRequest,
    ) -> SequenceAlignmentResponse:
        """Execute a pairwise alignment and return its API representation."""

        if not isinstance(request, SequenceAlignmentRequest):
            raise TypeError(
                "Alignment API service requires a "
                "SequenceAlignmentRequest."
            )

        first_sequence = BiologicalSequence(
            name=request.first_sequence.name,
            residues=request.first_sequence.residues,
            alphabet=request.first_sequence.alphabet,
            description=request.first_sequence.description,
        )

        second_sequence = BiologicalSequence(
            name=request.second_sequence.name,
            residues=request.second_sequence.residues,
            alphabet=request.second_sequence.alphabet,
            description=request.second_sequence.description,
        )

        if request.scoring.method == "simple":
            scoring_scheme = SimpleScoringScheme(
                alphabet=request.first_sequence.alphabet,
                match_score=request.scoring.match_score,
                mismatch_score=request.scoring.mismatch_score,
            )
        else:
            scoring_scheme = SubstitutionScoringScheme(
                substitution_matrix=BLOSUM62,
            )

        if request.gap.model == "linear":
            gap_penalty = LinearGapPenalty(
                gap_penalty=request.gap.gap_penalty,
            )
        else:
            gap_penalty = AffineGapPenalty(
                gap_open_penalty=request.gap.gap_open_penalty,
                gap_extension_penalty=request.gap.gap_extension_penalty,
            )

        result = self._alignment_service.align(
            first_sequence=first_sequence,
            second_sequence=second_sequence,
            scoring_scheme=scoring_scheme,
            gap_penalty=gap_penalty,
            alignment_type=request.alignment_type,
        )

        sequence_names = {
            first_sequence.identity.value: first_sequence.name,
            second_sequence.identity.value: second_sequence.name,
        }

        return SequenceAlignmentResponse.from_result(
            result=result,
            sequence_names=sequence_names,
        )
