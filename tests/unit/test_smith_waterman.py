
import pytest

from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.domain.sequences.biological_sequence import BiologicalSequence
from aditi.domain.sequences.alignment import AlignmentType
from aditi.modules.sequence_alignment.algorithms import SmithWaterman
from aditi.modules.sequence_alignment.scoring import (
    AffineGapPenalty,
    BLOSUM62,
    LinearGapPenalty,
    SimpleScoringScheme,
    SubstitutionScoringScheme,
)


def make_sequence(
    name: str,
    residues: str,
    alphabet: SequenceAlphabet = SequenceAlphabet.DNA,
) -> BiologicalSequence:
    return BiologicalSequence(
        name=name,
        residues=residues,
        alphabet=alphabet,
    )


def make_scoring_scheme() -> SimpleScoringScheme:
    return SimpleScoringScheme(
        alphabet=SequenceAlphabet.DNA,
        match_score=2,
        mismatch_score=-1,
    )


class TestSmithWaterman:

    def test_aligns_identical_sequences(self) -> None:
        result = SmithWaterman().align(
            make_sequence("first", "ACGT"),
            make_sequence("second", "ACGT"),
            make_scoring_scheme(),
            LinearGapPenalty(-2),
        )

        assert result.alignment_type is AlignmentType.LOCAL
        assert result.aligned_sequences[0].residues == "ACGT"
        assert result.aligned_sequences[1].residues == "ACGT"
        assert result.score.score == 8
        assert result.identical_positions == 4

    def test_identifies_matching_local_region(self) -> None:
        result = SmithWaterman().align(
            make_sequence("first", "TTACGTAA"),
            make_sequence("second", "GGACGTCC"),
            make_scoring_scheme(),
            LinearGapPenalty(-2),
        )

        first, second = result.aligned_sequences

        assert first.residues == "ACGT"
        assert second.residues == "ACGT"
        assert result.score.score == 8
        assert result.identical_positions == 4

    def test_preserves_original_sequence_positions(self) -> None:
        result = SmithWaterman().align(
            make_sequence("first", "TTACGTAA"),
            make_sequence("second", "GGACGTCC"),
            make_scoring_scheme(),
            LinearGapPenalty(-2),
        )

        first, second = result.aligned_sequences

        assert first.position_mapping == (2, 3, 4, 5)
        assert second.position_mapping == (2, 3, 4, 5)

    def test_aligns_sequences_with_a_local_gap(self) -> None:
        result = SmithWaterman().align(
            make_sequence("first", "ACGT"),
            make_sequence("second", "AGT"),
            make_scoring_scheme(),
            LinearGapPenalty(-1),
        )

        first, second = result.aligned_sequences

        assert first.residues == "ACGT"
        assert second.residues == "A-GT"
        assert first.position_mapping == (0, 1, 2, 3)
        assert second.position_mapping == (0, None, 1, 2)
        assert result.score.score == 5
        assert result.gap_count == 1

    def test_uses_affine_gap_penalties(self) -> None:
        result = SmithWaterman().align(
            make_sequence("first", "AAAAACCCCC"),
            make_sequence("second", "AAAAAGGGGGCCCCC"),
            SimpleScoringScheme(
                alphabet=SequenceAlphabet.DNA,
                match_score=2,
                mismatch_score=-3,
            ),
            AffineGapPenalty(
                gap_open_penalty=-5,
                gap_extension_penalty=-1,
            ),
        )

        first, second = result.aligned_sequences

        assert first.residues == "AAAAA-----CCCCC"
        assert second.residues == "AAAAAGGGGGCCCCC"
        assert first.gap_count == 5
        assert second.gap_count == 0
        assert result.score.score == 11
        assert result.score.gap_open_penalty == -5
        assert result.score.gap_extension_penalty == -1

    def test_uses_blosum62_for_protein_alignment(self) -> None:
        result = SmithWaterman().align(
            make_sequence(
                "first",
                "GGGMKWPPP",
                SequenceAlphabet.PROTEIN,
            ),
            make_sequence(
                "second",
                "TTMKWAAA",
                SequenceAlphabet.PROTEIN,
            ),
            SubstitutionScoringScheme(BLOSUM62),
            AffineGapPenalty(-10, -1),
        )

        first, second = result.aligned_sequences

        assert first.residues == "MKW"
        assert second.residues == "MKW"
        assert first.position_mapping == (3, 4, 5)
        assert second.position_mapping == (2, 3, 4)
        assert result.score.score == 21
        assert result.score.substitution_matrix == "BLOSUM62"
        assert result.identical_positions == 3

    def test_preserves_sequence_identities(self) -> None:
        first = make_sequence("first", "TTACGT")
        second = make_sequence("second", "GGACGT")

        result = SmithWaterman().align(
            first,
            second,
            make_scoring_scheme(),
            LinearGapPenalty(-2),
        )

        assert (
            result.aligned_sequences[0].sequence_identity
            == first.identity
        )
        assert (
            result.aligned_sequences[1].sequence_identity
            == second.identity
        )

    def test_rejects_different_sequence_alphabets(self) -> None:
        with pytest.raises(ValueError):
            SmithWaterman().align(
                make_sequence("first", "ACGT"),
                make_sequence(
                    "second",
                    "ACGU",
                    SequenceAlphabet.RNA,
                ),
                make_scoring_scheme(),
                LinearGapPenalty(-2),
            )

    def test_rejects_mismatched_scoring_alphabet(self) -> None:
        with pytest.raises(ValueError):
            SmithWaterman().align(
                make_sequence("first", "ACGT"),
                make_sequence("second", "ACGT"),
                SimpleScoringScheme(
                    alphabet=SequenceAlphabet.RNA,
                    match_score=2,
                    mismatch_score=-1,
                ),
                LinearGapPenalty(-2),
            )

    def test_rejects_invalid_first_input(self) -> None:
        with pytest.raises(TypeError):
            SmithWaterman().align(
                "ACGT",
                make_sequence("second", "ACGT"),
                make_scoring_scheme(),
                LinearGapPenalty(-2),
            )

    def test_rejects_invalid_scoring_scheme(self) -> None:
        with pytest.raises(TypeError):
            SmithWaterman().align(
                make_sequence("first", "ACGT"),
                make_sequence("second", "ACGT"),
                "invalid",
                LinearGapPenalty(-2),
            )

    def test_rejects_invalid_gap_penalty(self) -> None:
        with pytest.raises(TypeError):
            SmithWaterman().align(
                make_sequence("first", "ACGT"),
                make_sequence("second", "ACGT"),
                make_scoring_scheme(),
                -2,
            )

    def test_rejects_sequences_without_positive_local_alignment(self) -> None:
        with pytest.raises(ValueError, match="No positive-scoring"):
            SmithWaterman().align(
                make_sequence("first", "AAAA"),
                make_sequence("second", "CCCC"),
                SimpleScoringScheme(
                    alphabet=SequenceAlphabet.DNA,
                    match_score=1,
                    mismatch_score=-2,
                ),
                LinearGapPenalty(-2),
            )

    def test_resolves_equal_scoring_alignments_deterministically(self) -> None:
        result = SmithWaterman().align(
            make_sequence("first", "AA"),
            make_sequence("second", "A"),
            make_scoring_scheme(),
            LinearGapPenalty(-2),
        )

        first, second = result.aligned_sequences

        assert first.residues == "A"
        assert second.residues == "A"
        assert first.position_mapping == (0,)
        assert second.position_mapping == (0,)
        assert result.score.score == 2
