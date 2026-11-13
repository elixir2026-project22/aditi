
import pytest

from aditi.domain.sequences.alignment.alignment_score import (
    AlignmentScore,
)


def test_creates_simple_scoring_configuration() -> None:
    result = AlignmentScore(
        score=12,
        scoring_scheme="simple",
        match_score=2,
        mismatch_score=-1,
        gap_open_penalty=-2,
        gap_extension_penalty=-1,
    )

    assert result.score == 12
    assert result.match_score == 2
    assert result.mismatch_score == -1
    assert result.uses_substitution_matrix is False
    assert result.uses_affine_gaps is True


def test_creates_substitution_matrix_configuration() -> None:
    result = AlignmentScore(
        score=35.5,
        scoring_scheme="protein",
        substitution_matrix="BLOSUM62",
        gap_open_penalty=-10,
        gap_extension_penalty=-0.5,
    )

    assert result.score == 35.5
    assert result.substitution_matrix == "BLOSUM62"
    assert result.uses_substitution_matrix is True


def test_detects_equal_gap_penalties() -> None:
    result = AlignmentScore(
        score=8,
        scoring_scheme="simple",
        match_score=2,
        mismatch_score=-1,
        gap_open_penalty=-2,
        gap_extension_penalty=-2,
    )

    assert result.uses_affine_gaps is False


def test_allows_zero_gap_penalties() -> None:
    result = AlignmentScore(
        score=5,
        scoring_scheme="simple",
        match_score=1,
        mismatch_score=-1,
        gap_open_penalty=0,
        gap_extension_penalty=0,
    )

    assert result.gap_open_penalty == 0


@pytest.mark.parametrize(
    "score",
    [float("nan"), float("inf"), float("-inf")],
)
def test_rejects_non_finite_alignment_score(
    score: float,
) -> None:
    with pytest.raises(ValueError):
        AlignmentScore(
            score=score,
            scoring_scheme="simple",
            match_score=2,
            mismatch_score=-1,
            gap_open_penalty=-2,
            gap_extension_penalty=-1,
        )


@pytest.mark.parametrize(
    "penalty",
    [1, 0.5],
)
def test_rejects_positive_gap_penalties(
    penalty: float,
) -> None:
    with pytest.raises(ValueError):
        AlignmentScore(
            score=5,
            scoring_scheme="simple",
            match_score=2,
            mismatch_score=-1,
            gap_open_penalty=penalty,
            gap_extension_penalty=-1,
        )


def test_rejects_missing_mismatch_score() -> None:
    with pytest.raises(ValueError):
        AlignmentScore(
            score=5,
            scoring_scheme="simple",
            match_score=2,
            mismatch_score=None,
            gap_open_penalty=-2,
            gap_extension_penalty=-1,
        )


def test_rejects_missing_match_score() -> None:
    with pytest.raises(ValueError):
        AlignmentScore(
            score=5,
            scoring_scheme="simple",
            match_score=None,
            mismatch_score=-1,
            gap_open_penalty=-2,
            gap_extension_penalty=-1,
        )


def test_rejects_combined_matrix_and_simple_scoring() -> None:
    with pytest.raises(ValueError):
        AlignmentScore(
            score=5,
            scoring_scheme="protein",
            substitution_matrix="BLOSUM62",
            match_score=2,
            mismatch_score=-1,
            gap_open_penalty=-2,
            gap_extension_penalty=-1,
        )


def test_rejects_missing_scoring_configuration() -> None:
    with pytest.raises(ValueError):
        AlignmentScore(
            score=5,
            scoring_scheme="unknown",
            gap_open_penalty=-2,
            gap_extension_penalty=-1,
        )


def test_rejects_invalid_scoring_scheme() -> None:
    with pytest.raises(ValueError):
        AlignmentScore(
            score=5,
            scoring_scheme=" ",
            match_score=2,
            mismatch_score=-1,
            gap_open_penalty=-2,
            gap_extension_penalty=-1,
        )


def test_rejects_non_numeric_score() -> None:
    with pytest.raises(TypeError):
        AlignmentScore(
            score="high",
            scoring_scheme="simple",
            match_score=2,
            mismatch_score=-1,
            gap_open_penalty=-2,
            gap_extension_penalty=-1,
        )


def test_rejects_boolean_score() -> None:
    with pytest.raises(TypeError):
        AlignmentScore(
            score=True,
            scoring_scheme="simple",
            match_score=2,
            mismatch_score=-1,
            gap_open_penalty=-2,
            gap_extension_penalty=-1,
        )
