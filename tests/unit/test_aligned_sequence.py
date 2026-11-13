
import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.sequences.alignment.aligned_sequence import (
    AlignedSequence,
)


@pytest.fixture
def sequence_identity() -> EntityIdentity:
    return EntityIdentity.generate()


def test_creates_valid_aligned_sequence(
    sequence_identity: EntityIdentity,
) -> None:
    sequence = AlignedSequence(
        sequence_identity=sequence_identity,
        residues="AC-GT",
        position_mapping=(0, 1, None, 2, 3),
    )

    assert sequence.aligned_length == 5
    assert sequence.sequence_length == 4
    assert sequence.gap_count == 1
    assert sequence.ungapped_residues == "ACGT"


def test_maps_alignment_positions_to_original_positions(
    sequence_identity: EntityIdentity,
) -> None:
    sequence = AlignedSequence(
        sequence_identity=sequence_identity,
        residues="A-CG",
        position_mapping=(0, None, 1, 2),
    )

    assert sequence.original_position_at(0) == 0
    assert sequence.original_position_at(1) is None
    assert sequence.original_position_at(2) == 1
    assert sequence.original_position_at(3) == 2


def test_rejects_invalid_sequence_identity() -> None:
    with pytest.raises(TypeError):
        AlignedSequence(
            sequence_identity="invalid",
            residues="ACGT",
            position_mapping=(0, 1, 2, 3),
        )


@pytest.mark.parametrize(
    ("residues", "mapping"),
    [
        ("", ()),
        ("ACGT", (0, 1, 2)),
        ("ACGT", (0, 1, 2, None)),
        ("ACGT", (0, 1, 1, 3)),
        ("ACGT", (0, 2, 1, 3)),
        ("ACGT", (0, 1, 2, 4)),
        ("AC-G", (0, 1, 2, 3)),
        ("acgt", (0, 1, 2, 3)),
    ],
)
def test_rejects_invalid_alignment_data(
    sequence_identity: EntityIdentity,
    residues: str,
    mapping: tuple[int | None, ...],
) -> None:
    with pytest.raises(ValueError):
        AlignedSequence(
            sequence_identity=sequence_identity,
            residues=residues,
            position_mapping=mapping,
        )


@pytest.mark.parametrize("position", [-1, 4])
def test_rejects_out_of_range_alignment_positions(
    sequence_identity: EntityIdentity,
    position: int,
) -> None:
    sequence = AlignedSequence(
        sequence_identity=sequence_identity,
        residues="ACGT",
        position_mapping=(0, 1, 2, 3),
    )

    with pytest.raises(IndexError):
        sequence.original_position_at(position)


def test_rejects_non_integer_alignment_position(
    sequence_identity: EntityIdentity,
) -> None:
    sequence = AlignedSequence(
        sequence_identity=sequence_identity,
        residues="ACGT",
        position_mapping=(0, 1, 2, 3),
    )

    with pytest.raises(TypeError):
        sequence.original_position_at(1.5)


def test_rejects_boolean_alignment_position(
    sequence_identity: EntityIdentity,
) -> None:
    sequence = AlignedSequence(
        sequence_identity=sequence_identity,
        residues="ACGT",
        position_mapping=(0, 1, 2, 3),
    )

    with pytest.raises(TypeError):
        sequence.original_position_at(True)


def test_rejects_non_tuple_position_mapping(
    sequence_identity: EntityIdentity,
) -> None:
    with pytest.raises(TypeError):
        AlignedSequence(
            sequence_identity=sequence_identity,
            residues="ACGT",
            position_mapping=[0, 1, 2, 3],
        )
