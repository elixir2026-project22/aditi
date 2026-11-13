
import pytest

from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.domain.sequences.biological_sequence import BiologicalSequence
from aditi.domain.sequences.alignment import AlignmentType
from aditi.modules.sequence_alignment.algorithms import NeedlemanWunsch
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


class TestNeedlemanWunsch:

    def test_aligns_identical_sequences(self) -> None:
        algorithm = NeedlemanWunsch()

        result = algorithm.align(
            make_sequence("first", "ACGT"),
            make_sequence("second", "ACGT"),
            SimpleScoringScheme(
                alphabet=SequenceAlphabet.DNA,
                match_score=2,
                mismatch_score=-1,
            ),
            LinearGapPenalty(-2),
        )

        assert result.alignment_type is AlignmentType.GLOBAL
        assert result.aligned_sequences[0].residues == "ACGT"
        assert result.aligned_sequences[1].residues == "ACGT"
        assert result.score.score == 8
        assert result.identical_positions == 4

    def test_aligns_sequences_with_a_mismatch(self) -> None:
        result = NeedlemanWunsch().align(
            make_sequence("first", "ACGT"),
            make_sequence("second", "AGGT"),
            SimpleScoringScheme(
                alphabet=SequenceAlphabet.DNA,
                match_score=2,
                mismatch_score=-1,
            ),
            LinearGapPenalty(-2),
        )

        assert result.aligned_sequences[0].residues == "ACGT"
        assert result.aligned_sequences[1].residues == "AGGT"
        assert result.score.score == 5
        assert result.identical_positions == 3

    def test_aligns_sequences_with_a_gap(self) -> None:
        result = NeedlemanWunsch().align(
            make_sequence("first", "ACGT"),
            make_sequence("second", "AGT"),
            SimpleScoringScheme(
                alphabet=SequenceAlphabet.DNA,
                match_score=2,
                mismatch_score=-1,
            ),
            LinearGapPenalty(-2),
        )

        first, second = result.aligned_sequences

        assert first.residues == "ACGT"
        assert second.residues == "A-GT"
        assert first.position_mapping == (0, 1, 2, 3)
        assert second.position_mapping == (0, None, 1, 2)
        assert result.score.score == 4
        assert result.gap_count == 1

    def test_preserves_sequence_identities(self) -> None:
        first = make_sequence("first", "AC")
        second = make_sequence("second", "AG")

        result = NeedlemanWunsch().align(
            first,
            second,
            SimpleScoringScheme(
                alphabet=SequenceAlphabet.DNA,
                match_score=2,
                mismatch_score=-1,
            ),
            LinearGapPenalty(-2),
        )

        assert result.aligned_sequences[0].sequence_identity == first.identity
        assert result.aligned_sequences[1].sequence_identity == second.identity

    def test_uses_affine_gap_penalties(self) -> None:
        result = NeedlemanWunsch().align(
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

        assert first.aligned_length == second.aligned_length
        assert first.gap_count == 5
        assert second.gap_count == 0
        assert result.score.score == 11
        assert result.score.gap_open_penalty == -5
        assert result.score.gap_extension_penalty == -1

    def test_uses_blosum62_for_protein_alignment(self) -> None:
        result = NeedlemanWunsch().align(
            make_sequence(
                "first",
                "MKW",
                SequenceAlphabet.PROTEIN,
            ),
            make_sequence(
                "second",
                "MKW",
                SequenceAlphabet.PROTEIN,
            ),
            SubstitutionScoringScheme(BLOSUM62),
            AffineGapPenalty(-10, -1),
        )

        assert result.aligned_sequences[0].residues == "MKW"
        assert result.aligned_sequences[1].residues == "MKW"
        assert result.score.score == 21
        assert result.score.substitution_matrix == "BLOSUM62"
        assert result.identical_positions == 3

    def test_rejects_different_sequence_alphabets(self) -> None:
        with pytest.raises(ValueError):
            NeedlemanWunsch().align(
                make_sequence("first", "ACGT"),
                make_sequence(
                    "second",
                    "ACGU",
                    SequenceAlphabet.RNA,
                ),
                SimpleScoringScheme(
                    alphabet=SequenceAlphabet.DNA,
                    match_score=2,
                    mismatch_score=-1,
                ),
                LinearGapPenalty(-2),
            )

    def test_rejects_mismatched_scoring_alphabet(self) -> None:
        with pytest.raises(ValueError):
            NeedlemanWunsch().align(
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
            NeedlemanWunsch().align(
                "ACGT",
                make_sequence("second", "ACGT"),
                SimpleScoringScheme(
                    alphabet=SequenceAlphabet.DNA,
                    match_score=2,
                    mismatch_score=-1,
                ),
                LinearGapPenalty(-2),
            )

    def test_rejects_invalid_scoring_scheme(self) -> None:
        with pytest.raises(TypeError):
            NeedlemanWunsch().align(
                make_sequence("first", "ACGT"),
                make_sequence("second", "ACGT"),
                "invalid",
                LinearGapPenalty(-2),
            )

    def test_rejects_invalid_gap_penalty(self) -> None:
        with pytest.raises(TypeError):
            NeedlemanWunsch().align(
                make_sequence("first", "ACGT"),
                make_sequence("second", "ACGT"),
                SimpleScoringScheme(
                    alphabet=SequenceAlphabet.DNA,
                    match_score=2,
                    mismatch_score=-1,
                ),
                -2,
            )
