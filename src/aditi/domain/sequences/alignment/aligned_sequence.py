
from __future__ import annotations

from dataclasses import dataclass

from aditi.domain.entities.identity import EntityIdentity


@dataclass(frozen=True, slots=True)
class AlignedSequence:
    """
    Represents one biological sequence participating in an alignment.

    Alignment positions include gap characters. Original sequence
    positions refer only to biological residues.

    Position mapping uses zero-based indexing. Gaps map to None.
    Mapped positions must be contiguous and preserve residue order,
    but may begin at a non-zero offset for local alignments.
    """

    sequence_identity: EntityIdentity
    residues: str
    position_mapping: tuple[int | None, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.sequence_identity, EntityIdentity):
            raise TypeError(
                "Sequence identity must be an EntityIdentity instance."
            )

        if not isinstance(self.residues, str) or not self.residues:
            raise ValueError(
                "Aligned residues must be a non-empty string."
            )

        if self.residues != self.residues.upper():
            raise ValueError(
                "Aligned residues must contain uppercase symbols."
            )

        if not isinstance(self.position_mapping, tuple):
            raise TypeError(
                "Position mapping must be provided as a tuple."
            )

        if len(self.position_mapping) != len(self.residues):
            raise ValueError(
                "Position mapping length must match aligned residue length."
            )

        original_positions: list[int] = []

        for residue, position in zip(
            self.residues,
            self.position_mapping,
        ):
            if residue == "-":
                if position is not None:
                    raise ValueError(
                        "Alignment gaps must map to None."
                    )
                continue

            if position is None:
                raise ValueError(
                    "Biological residues must map to an original position."
                )

            if (
                isinstance(position, bool)
                or not isinstance(position, int)
                or position < 0
            ):
                raise ValueError(
                    "Original sequence positions must be non-negative integers."
                )

            original_positions.append(position)

        if original_positions:
            expected_positions = list(
                range(
                    original_positions[0],
                    original_positions[0] + len(original_positions),
                )
            )

            if original_positions != expected_positions:
                raise ValueError(
                    "Original sequence positions must be contiguous "
                    "and preserve biological residue order."
                )

    @property
    def aligned_length(self) -> int:
        """Return the number of alignment columns."""
        return len(self.residues)

    @property
    def sequence_length(self) -> int:
        """Return the number of biological residues in this aligned segment."""
        return len(self.position_mapping) - self.gap_count

    @property
    def gap_count(self) -> int:
        """Return the number of alignment gaps."""
        return self.residues.count("-")

    @property
    def ungapped_residues(self) -> str:
        """Return the biological sequence without alignment gaps."""
        return self.residues.replace("-", "")

    def original_position_at(
        self,
        alignment_position: int,
    ) -> int | None:
        """Map an alignment column to its original sequence position."""

        if (
            isinstance(alignment_position, bool)
            or not isinstance(alignment_position, int)
        ):
            raise TypeError(
                "Alignment position must be an integer."
            )

        if not 0 <= alignment_position < self.aligned_length:
            raise IndexError(
                "Alignment position is outside the aligned sequence."
            )

        return self.position_mapping[alignment_position]
