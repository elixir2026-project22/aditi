
import pytest

from aditi.modules.sequence_alignment.scoring.gap_penalty import (
    AffineGapPenalty,
    LinearGapPenalty,
)


class TestLinearGapPenalty:

    def test_calculates_single_position_gap(self) -> None:
        penalty = LinearGapPenalty(gap_penalty=-2)

        assert penalty.penalty(1) == -2

    def test_calculates_multiple_position_gap(self) -> None:
        penalty = LinearGapPenalty(gap_penalty=-2)

        assert penalty.penalty(4) == -8

    def test_accepts_zero_penalty(self) -> None:
        penalty = LinearGapPenalty(gap_penalty=0)

        assert penalty.penalty(5) == 0

    def test_rejects_positive_penalty(self) -> None:
        with pytest.raises(ValueError):
            LinearGapPenalty(gap_penalty=2)

    def test_rejects_non_numeric_penalty(self) -> None:
        with pytest.raises(TypeError):
            LinearGapPenalty(gap_penalty="invalid")

    def test_rejects_non_finite_penalty(self) -> None:
        with pytest.raises(ValueError):
            LinearGapPenalty(gap_penalty=float("inf"))

    def test_rejects_zero_gap_length(self) -> None:
        penalty = LinearGapPenalty(gap_penalty=-2)

        with pytest.raises(ValueError):
            penalty.penalty(0)

    def test_rejects_negative_gap_length(self) -> None:
        penalty = LinearGapPenalty(gap_penalty=-2)

        with pytest.raises(ValueError):
            penalty.penalty(-1)

    def test_rejects_non_integer_gap_length(self) -> None:
        penalty = LinearGapPenalty(gap_penalty=-2)

        with pytest.raises(TypeError):
            penalty.penalty(2.5)

    def test_rejects_boolean_gap_length(self) -> None:
        penalty = LinearGapPenalty(gap_penalty=-2)

        with pytest.raises(TypeError):
            penalty.penalty(True)


class TestAffineGapPenalty:

    def test_calculates_single_position_gap(self) -> None:
        penalty = AffineGapPenalty(
            gap_open_penalty=-5,
            gap_extension_penalty=-1,
        )

        assert penalty.penalty(1) == -5

    def test_calculates_multiple_position_gap(self) -> None:
        penalty = AffineGapPenalty(
            gap_open_penalty=-5,
            gap_extension_penalty=-1,
        )

        assert penalty.penalty(4) == -8

    def test_calculates_long_gap(self) -> None:
        penalty = AffineGapPenalty(
            gap_open_penalty=-10,
            gap_extension_penalty=-2,
        )

        assert penalty.penalty(6) == -20

    def test_accepts_zero_penalties(self) -> None:
        penalty = AffineGapPenalty(
            gap_open_penalty=0,
            gap_extension_penalty=0,
        )

        assert penalty.penalty(5) == 0

    def test_rejects_positive_opening_penalty(self) -> None:
        with pytest.raises(ValueError):
            AffineGapPenalty(
                gap_open_penalty=2,
                gap_extension_penalty=-1,
            )

    def test_rejects_positive_extension_penalty(self) -> None:
        with pytest.raises(ValueError):
            AffineGapPenalty(
                gap_open_penalty=-5,
                gap_extension_penalty=1,
            )

    def test_rejects_non_numeric_penalty(self) -> None:
        with pytest.raises(TypeError):
            AffineGapPenalty(
                gap_open_penalty="invalid",
                gap_extension_penalty=-1,
            )

    def test_rejects_non_finite_penalty(self) -> None:
        with pytest.raises(ValueError):
            AffineGapPenalty(
                gap_open_penalty=-5,
                gap_extension_penalty=float("nan"),
            )

    def test_rejects_invalid_gap_length(self) -> None:
        penalty = AffineGapPenalty(
            gap_open_penalty=-5,
            gap_extension_penalty=-1,
        )

        with pytest.raises(ValueError):
            penalty.penalty(0)

    def test_identifies_linear_penalty_configuration(self) -> None:
        penalty = AffineGapPenalty(
            gap_open_penalty=-2,
            gap_extension_penalty=-2,
        )

        assert penalty.is_linear is True

    def test_identifies_affine_penalty_configuration(self) -> None:
        penalty = AffineGapPenalty(
            gap_open_penalty=-5,
            gap_extension_penalty=-1,
        )

        assert penalty.is_linear is False
