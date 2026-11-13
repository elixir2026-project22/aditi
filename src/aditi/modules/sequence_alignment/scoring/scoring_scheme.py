
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.modules.sequence_alignment.scoring.substitution_matrix import (
    SubstitutionMatrix,
)


class ScoringScheme(ABC):
    """Contract for biological residue substitution scoring."""

    @abstractmethod
    def score(
        self,
        first_residue: str,
        second_residue: str,
    ) -> float:
        """Return the substitution score for two residues."""
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class SimpleScoringScheme(ScoringScheme):
    """Match/mismatch scoring for nucleotide or protein sequences."""

    alphabet: SequenceAlphabet
    match_score: float
    mismatch_score: float

    def __post_init__(self) -> None:
        if not isinstance(self.alphabet, SequenceAlphabet):
            raise TypeError(
                "Alphabet must be a SequenceAlphabet instance."
            )

        self._validate_score(self.match_score, "Match score")
        self._validate_score(self.mismatch_score, "Mismatch score")

    @staticmethod
    def _validate_score(value: float, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be numeric.")

        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite.")

    def score(
        self,
        first_residue: str,
        second_residue: str,
    ) -> float:
        self.alphabet.validate_residues(first_residue)
        self.alphabet.validate_residues(second_residue)

        if len(first_residue) != 1 or len(second_residue) != 1:
            raise ValueError(
                "Residue scoring requires exactly one symbol per input."
            )

        return (
            self.match_score
            if first_residue == second_residue
            else self.mismatch_score
        )


@dataclass(frozen=True, slots=True)
class SubstitutionScoringScheme(ScoringScheme):
    """Scores residue pairs using a SubstitutionMatrix."""

    substitution_matrix: SubstitutionMatrix

    def __post_init__(self) -> None:
        if not isinstance(
            self.substitution_matrix,
            SubstitutionMatrix,
        ):
            raise TypeError(
                "Substitution matrix must be a SubstitutionMatrix instance."
            )

    @property
    def alphabet(self) -> SequenceAlphabet:
        """Return the alphabet supported by the matrix."""
        return self.substitution_matrix.alphabet

    @property
    def matrix_name(self) -> str:
        """Return the name of the substitution matrix."""
        return self.substitution_matrix.name

    def score(
        self,
        first_residue: str,
        second_residue: str,
    ) -> float:
        return self.substitution_matrix.score(
            first_residue,
            second_residue,
        )
