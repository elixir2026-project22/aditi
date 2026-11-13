
import pytest

from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.modules.sequence_alignment.scoring.substitution_matrix import (
    BLOSUM62,
    SubstitutionMatrix,
)


class TestBlosum62:

    def test_has_expected_name(self) -> None:
        assert BLOSUM62.name == "BLOSUM62"

    def test_contains_twenty_standard_amino_acids(self) -> None:
        assert len(BLOSUM62.residues) == 20

    def test_scores_identical_alanine(self) -> None:
        assert BLOSUM62.score("A", "A") == 4

    def test_scores_identical_tryptophan(self) -> None:
        assert BLOSUM62.score("W", "W") == 11

    def test_scores_known_residue_pair(self) -> None:
        assert BLOSUM62.score("W", "F") == 1

    def test_matrix_is_symmetric(self) -> None:
        assert BLOSUM62.score("A", "R") == BLOSUM62.score("R", "A")

    def test_rejects_unsupported_ambiguous_residue(self) -> None:
        with pytest.raises(KeyError):
            BLOSUM62.score("X", "A")

    def test_matrix_scores_are_immutable(self) -> None:
        with pytest.raises(TypeError):
            BLOSUM62.scores[("A", "A")] = 100


class TestSubstitutionMatrix:

    def test_rejects_empty_matrix(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix(
                name="EMPTY",
                alphabet=SequenceAlphabet.PROTEIN,
                scores={},
            )

    def test_rejects_incomplete_matrix(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix(
                name="INCOMPLETE",
                alphabet=SequenceAlphabet.PROTEIN,
                scores={
                    ("A", "A"): 2,
                    ("A", "R"): -1,
                    ("R", "A"): -1,
                },
            )

    def test_rejects_asymmetric_matrix(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix(
                name="ASYMMETRIC",
                alphabet=SequenceAlphabet.PROTEIN,
                scores={
                    ("A", "A"): 2,
                    ("A", "R"): -1,
                    ("R", "A"): 1,
                    ("R", "R"): 3,
                },
            )

    def test_rejects_invalid_residue(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix(
                name="INVALID",
                alphabet=SequenceAlphabet.PROTEIN,
                scores={
                    ("A", "*"): 2,
                },
            )

    def test_rejects_non_finite_score(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix(
                name="NONFINITE",
                alphabet=SequenceAlphabet.PROTEIN,
                scores={
                    ("A", "A"): float("inf"),
                },
            )

    def test_rejects_invalid_matrix_name(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix(
                name=" ",
                alphabet=SequenceAlphabet.PROTEIN,
                scores={
                    ("A", "A"): 2,
                },
            )

    def test_parses_ncbi_format_matrix(self) -> None:
        matrix = SubstitutionMatrix.from_ncbi_text(
            """
                A R
                A  2 -1
                R -1  3
            """,
            name="CUSTOM",
            alphabet=SequenceAlphabet.PROTEIN,
        )

        assert matrix.score("A", "A") == 2
        assert matrix.score("A", "R") == -1
        assert matrix.score("R", "R") == 3

    def test_parser_ignores_comment_lines(self) -> None:
        matrix = SubstitutionMatrix.from_ncbi_text(
            """
                # Example matrix
                A R
                # Residue scores
                A  2 -1
                R -1  3
            """,
            name="CUSTOM",
            alphabet=SequenceAlphabet.PROTEIN,
        )

        assert matrix.score("R", "A") == -1

    def test_parser_rejects_missing_rows(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix.from_ncbi_text(
                """
                    A R
                    A 2 -1
                """,
                name="INCOMPLETE",
                alphabet=SequenceAlphabet.PROTEIN,
            )

    def test_parser_rejects_invalid_score(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix.from_ncbi_text(
                """
                    A R
                    A 2 invalid
                    R -1 3
                """,
                name="INVALID",
                alphabet=SequenceAlphabet.PROTEIN,
            )

    def test_parser_rejects_duplicate_header_symbols(self) -> None:
        with pytest.raises(ValueError):
            SubstitutionMatrix.from_ncbi_text(
                """
                    A A
                    A 2 2
                """,
                name="DUPLICATE",
                alphabet=SequenceAlphabet.PROTEIN,
            )

    def test_rejects_multi_character_score_input(self) -> None:
        with pytest.raises(ValueError):
            BLOSUM62.score("AA", "R")
