
from __future__ import annotations

from aditi.domain.sequences.alignment import (
    AlignmentResult,
    AlignmentType,
)
from aditi.domain.sequences.biological_sequence import BiologicalSequence
from aditi.modules.sequence_alignment.algorithms import (
    NeedlemanWunsch,
    SmithWaterman,
)
from aditi.modules.sequence_alignment.scoring.gap_penalty import GapPenalty
from aditi.modules.sequence_alignment.scoring.scoring_scheme import ScoringScheme


class AlignmentService:
    """
    Provides a unified interface for pairwise sequence alignment.

    The service delegates computation to the appropriate alignment
    algorithm while keeping algorithm selection separate from
    application and API layers.
    """

    def __init__(self) -> None:
        self._global_aligner = NeedlemanWunsch()
        self._local_aligner = SmithWaterman()

    def align(
        self,
        first_sequence: BiologicalSequence,
        second_sequence: BiologicalSequence,
        scoring_scheme: ScoringScheme,
        gap_penalty: GapPenalty,
        alignment_type: AlignmentType = AlignmentType.GLOBAL,
    ) -> AlignmentResult:
        """
        Align two biological sequences using the requested strategy.

        GLOBAL:
            Aligns both complete sequences using Needleman-Wunsch.

        LOCAL:
            Identifies the highest-scoring matching regions using
            Smith-Waterman.
        """

        if not isinstance(alignment_type, AlignmentType):
            raise TypeError(
                "Alignment type must be an AlignmentType instance."
            )

        if alignment_type is AlignmentType.GLOBAL:
            return self._global_aligner.align(
                first_sequence,
                second_sequence,
                scoring_scheme,
                gap_penalty,
            )

        if alignment_type is AlignmentType.LOCAL:
            return self._local_aligner.align(
                first_sequence,
                second_sequence,
                scoring_scheme,
                gap_penalty,
            )

        raise ValueError(
            f"Unsupported pairwise alignment type: {alignment_type.value}."
        )
