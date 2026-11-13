
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from aditi.domain.sequences.alignment.aligned_sequence import (
    AlignedSequence,
)
from aditi.domain.sequences.alignment.alignment_score import (
    AlignmentScore,
)


class AlignmentType(str, Enum):
    GLOBAL = "global"
    LOCAL = "local"
    MULTIPLE = "multiple"


@dataclass(frozen=True, slots=True)
class AlignmentResult:
    """
    Represents the result of a biological sequence alignment.

    Pairwise alignments contain exactly two aligned sequences.
    Multiple sequence alignment results contain at least two.

    Statistics are calculated from the aligned sequences.
    Similarity is optional because its interpretation depends
    on the scoring model.
    """

    aligned_sequences: tuple[AlignedSequence, ...]
    alignment_type: AlignmentType
    score: AlignmentScore

    identical_positions: int
    similar_positions: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.aligned_sequences, tuple):
            raise TypeError(
                "Aligned sequences must be provided as a tuple."
            )

        if len(self.aligned_sequences) < 2:
            raise ValueError(
                "An alignment must contain at least two sequences."
            )

        if not all(
            isinstance(sequence, AlignedSequence)
            for sequence in self.aligned_sequences
        ):
            raise TypeError(
                "All aligned sequences must be AlignedSequence instances."
            )

        if not isinstance(self.alignment_type, AlignmentType):
            raise TypeError(
                "Alignment type must be an AlignmentType instance."
            )

        if not isinstance(self.score, AlignmentScore):
            raise TypeError(
                "Score must be an AlignmentScore instance."
            )

        if (
            isinstance(self.identical_positions, bool)
            or not isinstance(self.identical_positions, int)
            or self.identical_positions < 0
        ):
            raise ValueError(
                "Identical positions must be a non-negative integer."
            )

        if self.similar_positions is not None:
            if (
                isinstance(self.similar_positions, bool)
                or not isinstance(self.similar_positions, int)
                or self.similar_positions < 0
            ):
                raise ValueError(
                    "Similar positions must be a non-negative integer."
                )

        aligned_lengths = {
            sequence.aligned_length
            for sequence in self.aligned_sequences
        }

        if len(aligned_lengths) != 1:
            raise ValueError(
                "All aligned sequences must have the same alignment length."
            )

        identities = [
            sequence.sequence_identity
            for sequence in self.aligned_sequences
        ]

        if len(identities) != len(set(identities)):
            raise ValueError(
                "An alignment cannot contain duplicate sequence identities."
            )

        if self.identical_positions > self.alignment_length:
            raise ValueError(
                "Identical positions cannot exceed alignment length."
            )

        if (
            self.similar_positions is not None
            and self.similar_positions > self.alignment_length
        ):
            raise ValueError(
                "Similar positions cannot exceed alignment length."
            )

        if (
            self.similar_positions is not None
            and self.similar_positions < self.identical_positions
        ):
            raise ValueError(
                "Similar positions cannot be fewer than identical positions."
            )

    @property
    def alignment_length(self) -> int:
        """Return the number of alignment columns."""
        return self.aligned_sequences[0].aligned_length

    @property
    def sequence_count(self) -> int:
        """Return the number of sequences in the alignment."""
        return len(self.aligned_sequences)

    @property
    def gap_count(self) -> int:
        """Return the total number of gap characters."""
        return sum(
            sequence.gap_count
            for sequence in self.aligned_sequences
        )

    @property
    def gap_percentage(self) -> float:
        """Return the percentage of alignment cells containing gaps."""
        total_cells = (
            self.alignment_length * self.sequence_count
        )

        return (
            self.gap_count / total_cells * 100
            if total_cells
            else 0.0
        )

    @property
    def identity_percentage(self) -> float:
        """
        Return the percentage of columns containing identical
        residues across every aligned sequence.

        This is a column-based statistic, not a pairwise
        identity average.
        """
        return (
            self.identical_positions / self.alignment_length * 100
            if self.alignment_length
            else 0.0
        )

    @property
    def similarity_percentage(self) -> float | None:
        """Return the similarity percentage when available."""
        if self.similar_positions is None:
            return None

        return (
            self.similar_positions / self.alignment_length * 100
            if self.alignment_length
            else 0.0
        )
