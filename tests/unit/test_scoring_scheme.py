
import pytest

from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.modules.sequence_alignment.scoring import (
    BLOSUM62,
    SimpleScoringScheme,
    SubstitutionMatrix,
    SubstitutionScoringScheme,
)


class TestSimpleScoringScheme:

    def test_returns_match_score(self) -> None:
        scheme = SimpleScoringScheme(
            alphabet=SequenceAlphabet.DNA,
            match_score=2,
            mismatch_score=-1,
        )

        assert scheme.score("A", "A") == 2

    def test_returns_mismatch_score(self) -> None:
        scheme = SimpleScoringScheme(
            alphabet=SequenceAlphabet.DNA,
            match_score=2,
            mismatch_score=-1,
        )

        assert scheme.score("A", "G") == -1

    def test_supports_rna(self) -> None:
        scheme = SimpleScoringScheme(
            alphabet=SequenceAlphabet.RNA,
            match_score=3,
            mismatch_score=-2,
        )

        assert scheme.score("U", "U") == 3

    def test_supports_protein(self) -> None:
        scheme = SimpleScoringScheme(
            alphabet=SequenceAlphabet.PROTEIN,
            match_score=2,
            mismatch_score=-1,
        )

        assert scheme.score("W", "F") == -1

    def test_rejects_invalid_residue(self) -> None:
        scheme = SimpleScoringScheme(
            alphabet=SequenceAlphabet.DNA,
            match_score=2,
            mismatch_score=-1,
        )

        with pytest.raises(ValueError):
            scheme.score("A", "X")

    def test_rejects_multiple_residues(self) -> None:
        scheme = SimpleScoringScheme(
            alphabet=SequenceAlphabet.DNA,
            match_score=2,
            mismatch_score=-1,
        )

        with pytest.raises(ValueError):
            scheme.score("AA", "A")

    def test_rejects_non_finite_match_score(self) -> None:
        with pytest.raises(ValueError):
            SimpleScoringScheme(
                alphabet=SequenceAlphabet.DNA,
                match_score=float("inf"),
                mismatch_score=-1,
            )

    def test_rejects_boolean_score(self) -> None:
        with pytest.raises(TypeError):
            SimpleScoringScheme(
                alphabet=SequenceAlphabet.DNA,
                match_score=True,
                mismatch_score=-1,
            )


class TestSubstitutionScoringScheme:

    def test_scores_using_blosum62(self) -> None:
        scheme = SubstitutionScoringScheme(
            substitution_matrix=BLOSUM62,
        )

        assert scheme.score("A", "A") == 4
        assert scheme.score("W", "W") == 11
        assert scheme.score("W", "F") == 1

    def test_exposes_matrix_name(self) -> None:
        scheme = SubstitutionScoringScheme(
            substitution_matrix=BLOSUM62,
        )

        assert scheme.matrix_name == "BLOSUM62"

    def test_exposes_matrix_alphabet(self) -> None:
        scheme = SubstitutionScoringScheme(
            substitution_matrix=BLOSUM62,
        )

        assert scheme.alphabet is SequenceAlphabet.PROTEIN

    def test_rejects_unsupported_matrix_residue(self) -> None:
        scheme = SubstitutionScoringScheme(
            substitution_matrix=BLOSUM62,
        )

        with pytest.raises(KeyError):
            scheme.score("X", "A")

    def test_rejects_invalid_matrix_type(self) -> None:
        with pytest.raises(TypeError):
            SubstitutionScoringScheme(
                substitution_matrix="BLOSUM62",
            )

    def test_supports_custom_matrix(self) -> None:
        matrix = SubstitutionMatrix.from_ncbi_text(
            """
                A R
                A 2 -1
                R -1 3
            """,
            name="CUSTOM",
            alphabet=SequenceAlphabet.PROTEIN,
        )

        scheme = SubstitutionScoringScheme(
            substitution_matrix=matrix,
        )

        assert scheme.score("A", "A") == 2
        assert scheme.score("A", "R") == -1
