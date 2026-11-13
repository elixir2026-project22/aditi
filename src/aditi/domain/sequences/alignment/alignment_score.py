
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AlignmentScore:
    """
    Stores an alignment score and the scoring configuration
    used to produce it.

    Supports either:
    - Substitution-matrix scoring.
    - Simple match/mismatch scoring.

    Gap penalties use the conventional non-positive representation.
    """

    score: float
    scoring_scheme: str

    gap_open_penalty: float
    gap_extension_penalty: float

    substitution_matrix: str | None = None

    match_score: float | None = None
    mismatch_score: float | None = None

    def __post_init__(self) -> None:
        self._validate_finite_number(
            self.score,
            "Alignment score",
        )

        self._validate_name(
            self.scoring_scheme,
            "Scoring scheme",
        )

        self._validate_penalty(
            self.gap_open_penalty,
            "Gap opening penalty",
        )

        self._validate_penalty(
            self.gap_extension_penalty,
            "Gap extension penalty",
        )

        if self.substitution_matrix is not None:
            self._validate_name(
                self.substitution_matrix,
                "Substitution matrix",
            )

        if (
            (self.match_score is None)
            != (self.mismatch_score is None)
        ):
            raise ValueError(
                "Match and mismatch scores must either both "
                "be provided or both be omitted."
            )

        if self.match_score is not None:
            self._validate_finite_number(
                self.match_score,
                "Match score",
            )

            self._validate_finite_number(
                self.mismatch_score,
                "Mismatch score",
            )

        if (
            self.substitution_matrix is not None
            and self.match_score is not None
        ):
            raise ValueError(
                "Substitution matrix scoring and simple "
                "match/mismatch scoring cannot be combined."
            )

        if (
            self.substitution_matrix is None
            and self.match_score is None
        ):
            raise ValueError(
                "Either a substitution matrix or both "
                "match and mismatch scores must be provided."
            )

    @staticmethod
    def _validate_finite_number(
        value: float,
        field_name: str,
    ) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            raise TypeError(
                f"{field_name} must be a numeric value."
            )

        if not math.isfinite(value):
            raise ValueError(
                f"{field_name} must be finite."
            )

    @classmethod
    def _validate_penalty(
        cls,
        value: float,
        field_name: str,
    ) -> None:
        cls._validate_finite_number(
            value,
            field_name,
        )

        if value > 0:
            raise ValueError(
                f"{field_name} must be zero or negative."
            )

    @staticmethod
    def _validate_name(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} must be a non-empty string."
            )

        if value != value.strip():
            raise ValueError(
                f"{field_name} cannot contain leading "
                "or trailing whitespace."
            )

    @property
    def uses_substitution_matrix(self) -> bool:
        """Return whether a substitution matrix was used."""
        return self.substitution_matrix is not None

    @property
    def uses_affine_gaps(self) -> bool:
        """Return whether gap opening and extension penalties differ."""
        return self.gap_open_penalty != self.gap_extension_penalty
