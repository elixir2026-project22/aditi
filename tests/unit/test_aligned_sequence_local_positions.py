
import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.sequences.alignment import AlignedSequence


def make_identity() -> EntityIdentity:
    return EntityIdentity()


def test_accepts_mapping_starting_at_nonzero_offset() -> None:
    sequence = AlignedSequence(
        sequence_identity=make_identity(),
        residues="AC-GT",
        position_mapping=(5, 6, None, 7, 8),
    )

    assert sequence.original_position_at(0) == 5
    assert sequence.original_position_at(1) == 6
    assert sequence.original_position_at(2) is None
    assert sequence.original_position_at(3) == 7
    assert sequence.original_position_at(4) == 8


def test_accepts_mapping_starting_at_zero() -> None:
    sequence = AlignedSequence(
        sequence_identity=make_identity(),
        residues="A-CG",
        position_mapping=(0, None, 1, 2),
    )

    assert sequence.ungapped_residues == "ACG"


def test_rejects_non_contiguous_original_positions() -> None:
    with pytest.raises(ValueError):
        AlignedSequence(
            sequence_identity=make_identity(),
            residues="ACGT",
            position_mapping=(5, 6, 8, 9),
        )


def test_rejects_original_positions_out_of_order() -> None:
    with pytest.raises(ValueError):
        AlignedSequence(
            sequence_identity=make_identity(),
            residues="ACGT",
            position_mapping=(5, 7, 6, 8),
        )


def test_sequence_length_counts_only_aligned_residues() -> None:
    sequence = AlignedSequence(
        sequence_identity=make_identity(),
        residues="A-C-G",
        position_mapping=(10, None, 11, None, 12),
    )

    assert sequence.sequence_length == 3
    assert sequence.gap_count == 2
