
import pytest

from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.domain.sequences.alignment import AlignmentType
from aditi.domain.sequences.biological_sequence import BiologicalSequence
from aditi.modules.sequence_alignment import AlignmentService
from aditi.modules.sequence_alignment.scoring import (
    LinearGapPenalty,
    SimpleScoringScheme,
)


def make_sequence(
    name: str,
    residues: str,
) -> BiologicalSequence:
    return BiologicalSequence(
        name=name,
        residues=residues,
        alphabet=SequenceAlphabet.DNA,
    )


def make_scoring_scheme() -> SimpleScoringScheme:
    return SimpleScoringScheme(
        alphabet=SequenceAlphabet.DNA,
        match_score=2,
        mismatch_score=-1,
    )


class TestAlignmentService:

    def test_uses_global_alignment_by_default(self) -> None:
        result = AlignmentService().align(
            make_sequence("first", "ACGT"),
            make_sequence("second", "AGT"),
            make_scoring_scheme(),
            LinearGapPenalty(-2),
        )

        assert result.alignment_type is AlignmentType.GLOBAL
        assert result.aligned_sequences[0].residues == "ACGT"
        assert result.aligned_sequences[1].residues == "A-GT"
        assert result.score.score == 4

    def test_uses_needleman_wunsch_for_global_alignment(self) -> None:
        result = AlignmentService().align(
            make_sequence("first", "ACGT"),
            make_sequence("second", "AGT"),
            make_scoring_scheme(),
            LinearGapPenalty(-2),
            AlignmentType.GLOBAL,
        )

        assert result.alignment_type is AlignmentType.GLOBAL
        assert result.aligned_sequences[0].residues == "ACGT"
        assert result.aligned_sequences[1].residues == "A-GT"

    def test_uses_smith_waterman_for_local_alignment(self) -> None:
        result = AlignmentService().align(
            make_sequence("first", "TTACGTAA"),
            make_sequence("second", "GGACGTCC"),
            make_scoring_scheme(),
            LinearGapPenalty(-2),
            AlignmentType.LOCAL,
        )

        first, second = result.aligned_sequences

        assert result.alignment_type is AlignmentType.LOCAL
        assert first.residues == "ACGT"
        assert second.residues == "ACGT"
        assert first.position_mapping == (2, 3, 4, 5)
        assert second.position_mapping == (2, 3, 4, 5)
        assert result.score.score == 8

    def test_preserves_sequence_identities(self) -> None:
        first = make_sequence("first", "TTACGT")
        second = make_sequence("second", "GGACGT")

        result = AlignmentService().align(
            first,
            second,
            make_scoring_scheme(),
            LinearGapPenalty(-2),
            AlignmentType.LOCAL,
        )

        assert result.aligned_sequences[0].sequence_identity == first.identity
        assert result.aligned_sequences[1].sequence_identity == second.identity

    def test_rejects_invalid_alignment_type(self) -> None:
        with pytest.raises(TypeError, match="AlignmentType"):
            AlignmentService().align(
                make_sequence("first", "ACGT"),
                make_sequence("second", "ACGT"),
                make_scoring_scheme(),
                LinearGapPenalty(-2),
                "global",
            )

    def test_rejects_multiple_alignment_type(self) -> None:
        with pytest.raises(ValueError, match="Unsupported pairwise"):
            AlignmentService().align(
                make_sequence("first", "ACGT"),
                make_sequence("second", "ACGT"),
                make_scoring_scheme(),
                LinearGapPenalty(-2),
                AlignmentType.MULTIPLE,
            )

    def test_propagates_sequence_validation_errors(self) -> None:
        with pytest.raises(ValueError, match="same biological alphabet"):
            AlignmentService().align(
                make_sequence("first", "ACGT"),
                BiologicalSequence(
                    name="second",
                    residues="ACGU",
                    alphabet=SequenceAlphabet.RNA,
                ),
                make_scoring_scheme(),
                LinearGapPenalty(-2),
                AlignmentType.GLOBAL,
            )

    def test_propagates_no_local_alignment_error(self) -> None:
        with pytest.raises(ValueError, match="No positive-scoring"):
            AlignmentService().align(
                make_sequence("first", "AAAA"),
                make_sequence("second", "CCCC"),
                SimpleScoringScheme(
                    alphabet=SequenceAlphabet.DNA,
                    match_score=1,
                    mismatch_score=-2,
                ),
                LinearGapPenalty(-2),
                AlignmentType.LOCAL,
            )
