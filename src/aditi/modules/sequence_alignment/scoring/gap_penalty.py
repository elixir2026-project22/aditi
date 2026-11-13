
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass


class GapPenalty(ABC):
    """Contract for biological sequence alignment gap penalties."""

    @abstractmethod
    def penalty(self, gap_length: int) -> float:
        """Return the penalty for a gap of the specified length."""
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class LinearGapPenalty(GapPenalty):
    """
    Applies a constant penalty for every position in a gap.

    Total penalty:
        gap_penalty * gap_length
    """

    gap_penalty: float

    def __post_init__(self) -> None:
        self._validate_penalty(
            self.gap_penalty,
            "Gap penalty",
        )

    def penalty(self, gap_length: int) -> float:
        self._validate_gap_length(gap_length)

        return self.gap_penalty * gap_length

    @staticmethod
    def _validate_gap_length(gap_length: int) -> None:
        if (
            isinstance(gap_length, bool)
            or not isinstance(gap_length, int)
        ):
            raise TypeError(
                "Gap length must be an integer."
            )

        if gap_length < 1:
            raise ValueError(
                "Gap length must be at least one."
            )

    @staticmethod
    def _validate_penalty(
        value: float,
        name: str,
    ) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            raise TypeError(
                f"{name} must be numeric."
            )

        if not math.isfinite(value):
            raise ValueError(
                f"{name} must be finite."
            )

        if value > 0:
            raise ValueError(
                f"{name} must be zero or negative."
            )


@dataclass(frozen=True, slots=True)
class AffineGapPenalty(GapPenalty):
    """
    Applies a gap-opening penalty and a gap-extension penalty.

    Total penalty:
        gap_open_penalty
        + (gap_length - 1) * gap_extension_penalty

    The opening penalty is applied once. The extension penalty
    is applied to every additional gap position.
    """

    gap_open_penalty: float
    gap_extension_penalty: float

    def __post_init__(self) -> None:
        LinearGapPenalty._validate_penalty(
            self.gap_open_penalty,
            "Gap opening penalty",
        )

        LinearGapPenalty._validate_penalty(
            self.gap_extension_penalty,
            "Gap extension penalty",
        )

    def penalty(self, gap_length: int) -> float:
        LinearGapPenalty._validate_gap_length(
            gap_length,
        )

        return (
            self.gap_open_penalty
            + (
                gap_length - 1
            ) * self.gap_extension_penalty
        )

    @property
    def is_linear(self) -> bool:
        """Return whether opening and extension penalties are equal."""
        return (
            self.gap_open_penalty
            == self.gap_extension_penalty
        )
