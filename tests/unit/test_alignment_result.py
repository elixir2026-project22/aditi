
import pytest

from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.sequences.alignment.aligned_sequence import (
    AlignedSequence,
)
from aditi.domain.sequences.alignment.alignment_result import (
    AlignmentResult,
    AlignmentType,
)
from aditi.domain.sequences.alignment.alignment_score import (
    AlignmentScore,
)


@pytest.fixture
def alignment_score() -> AlignmentScore:
    return AlignmentScore(
        score=8,
        scoring_scheme="simple",
        match_score=2,
        mismatch_score=-1,
        gap_open_penalty=-2,
        gap_extension_penalty=-1,
    )


@pytest.fixture
def aligned_sequences() -> tuple[AlignedSequence, AlignedSequence]:
    return (
        AlignedSequence(
            sequence_identity=EntityIdentity.generate(),
            residues="AC-GT",
            position_mapping=(0, 1, None, 2, 3),
        ),
        AlignedSequence(
            sequence_identity=EntityIdentity.generate(),
            residues="ATCGT",
            position_mapping=(0, 1, 2, 3, 4),
        ),
    )


def test_creates_valid_pairwise_alignment(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    result = AlignmentResult(
        aligned_sequences=aligned_sequences,
        alignment_type=AlignmentType.GLOBAL,
        score=alignment_score,
        identical_positions=3,
        similar_positions=4,
    )

    assert result.sequence_count == 2
    assert result.alignment_length == 5
    assert result.identical_positions == 3
    assert result.similar_positions == 4


def test_calculates_identity_percentage(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    result = AlignmentResult(
        aligned_sequences=aligned_sequences,
        alignment_type=AlignmentType.GLOBAL,
        score=alignment_score,
        identical_positions=3,
    )

    assert result.identity_percentage == 60.0


def test_calculates_gap_statistics(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    result = AlignmentResult(
        aligned_sequences=aligned_sequences,
        alignment_type=AlignmentType.GLOBAL,
        score=alignment_score,
        identical_positions=3,
    )

    assert result.gap_count == 1
    assert result.gap_percentage == 10.0


def test_calculates_similarity_percentage(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    result = AlignmentResult(
        aligned_sequences=aligned_sequences,
        alignment_type=AlignmentType.GLOBAL,
        score=alignment_score,
        identical_positions=3,
        similar_positions=4,
    )

    assert result.similarity_percentage == 80.0


def test_similarity_percentage_is_optional(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    result = AlignmentResult(
        aligned_sequences=aligned_sequences,
        alignment_type=AlignmentType.GLOBAL,
        score=alignment_score,
        identical_positions=3,
    )

    assert result.similarity_percentage is None


def test_supports_multiple_sequence_alignment(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    third_sequence = AlignedSequence(
        sequence_identity=EntityIdentity.generate(),
        residues="AC-GT",
        position_mapping=(0, 1, None, 2, 3),
    )

    result = AlignmentResult(
        aligned_sequences=(*aligned_sequences, third_sequence),
        alignment_type=AlignmentType.MULTIPLE,
        score=alignment_score,
        identical_positions=2,
    )

    assert result.sequence_count == 3


def test_rejects_fewer_than_two_sequences(
    alignment_score: AlignmentScore,
) -> None:
    sequence = AlignedSequence(
        sequence_identity=EntityIdentity.generate(),
        residues="ACGT",
        position_mapping=(0, 1, 2, 3),
    )

    with pytest.raises(ValueError):
        AlignmentResult(
            aligned_sequences=(sequence,),
            alignment_type=AlignmentType.GLOBAL,
            score=alignment_score,
            identical_positions=2,
        )


def test_rejects_unequal_alignment_lengths(
    alignment_score: AlignmentScore,
) -> None:
    first = AlignedSequence(
        sequence_identity=EntityIdentity.generate(),
        residues="ACGT",
        position_mapping=(0, 1, 2, 3),
    )

    second = AlignedSequence(
        sequence_identity=EntityIdentity.generate(),
        residues="ACG",
        position_mapping=(0, 1, 2),
    )

    with pytest.raises(ValueError):
        AlignmentResult(
            aligned_sequences=(first, second),
            alignment_type=AlignmentType.GLOBAL,
            score=alignment_score,
            identical_positions=2,
        )


def test_rejects_invalid_identical_positions(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    with pytest.raises(ValueError):
        AlignmentResult(
            aligned_sequences=aligned_sequences,
            alignment_type=AlignmentType.GLOBAL,
            score=alignment_score,
            identical_positions=6,
        )


def test_rejects_similarity_below_identity(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    with pytest.raises(ValueError):
        AlignmentResult(
            aligned_sequences=aligned_sequences,
            alignment_type=AlignmentType.GLOBAL,
            score=alignment_score,
            identical_positions=3,
            similar_positions=2,
        )


def test_rejects_duplicate_sequence_identity(
    alignment_score: AlignmentScore,
) -> None:
    identity = EntityIdentity.generate()

    first = AlignedSequence(
        sequence_identity=identity,
        residues="ACGT",
        position_mapping=(0, 1, 2, 3),
    )

    second = AlignedSequence(
        sequence_identity=identity,
        residues="ACGT",
        position_mapping=(0, 1, 2, 3),
    )

    with pytest.raises(ValueError):
        AlignmentResult(
            aligned_sequences=(first, second),
            alignment_type=AlignmentType.GLOBAL,
            score=alignment_score,
            identical_positions=4,
        )


def test_rejects_invalid_alignment_type(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    with pytest.raises(TypeError):
        AlignmentResult(
            aligned_sequences=aligned_sequences,
            alignment_type="global",
            score=alignment_score,
            identical_positions=3,
        )


def test_rejects_negative_identical_positions(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
    alignment_score: AlignmentScore,
) -> None:
    with pytest.raises(ValueError):
        AlignmentResult(
            aligned_sequences=aligned_sequences,
            alignment_type=AlignmentType.GLOBAL,
            score=alignment_score,
            identical_positions=-1,
        )


def test_rejects_invalid_score(
    aligned_sequences: tuple[AlignedSequence, AlignedSequence],
) -> None:
    with pytest.raises(TypeError):
        AlignmentResult(
            aligned_sequences=aligned_sequences,
            alignment_type=AlignmentType.GLOBAL,
            score=8,
            identical_positions=3,
        )
