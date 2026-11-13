
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from aditi.domain.sequences.alphabet import SequenceAlphabet


@dataclass(frozen=True, slots=True)
class SubstitutionMatrix:
    """
    Immutable substitution matrix for biological residue scoring.

    Matrix values are stored as ordered residue pairs. Symmetric
    matrices are validated when constructed.
    """

    name: str
    alphabet: SequenceAlphabet
    scores: Mapping[tuple[str, str], float]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Matrix name must be non-empty.")

        if self.name != self.name.strip():
            raise ValueError(
                "Matrix name cannot contain leading or trailing whitespace."
            )

        if not isinstance(self.alphabet, SequenceAlphabet):
            raise TypeError(
                "Alphabet must be a SequenceAlphabet instance."
            )

        if not isinstance(self.scores, Mapping):
            raise TypeError(
                "Matrix scores must be provided as a mapping."
            )

        normalized: dict[tuple[str, str], float] = {}

        for pair, value in self.scores.items():
            if (
                not isinstance(pair, tuple)
                or len(pair) != 2
                or not all(
                    isinstance(residue, str) and len(residue) == 1
                    for residue in pair
                )
            ):
                raise ValueError(
                    "Matrix keys must contain pairs of single residue symbols."
                )

            first, second = pair

            self.alphabet.validate_residues(first)
            self.alphabet.validate_residues(second)

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(
                    "Substitution scores must be numeric."
                )

            import math

            if not math.isfinite(value):
                raise ValueError(
                    "Substitution scores must be finite."
                )

            normalized[(first, second)] = float(value)

        if not normalized:
            raise ValueError("Substitution matrix cannot be empty.")

        residues = sorted({
            residue
            for pair in normalized
            for residue in pair
        })

        for first in residues:
            for second in residues:
                if (first, second) not in normalized:
                    raise ValueError(
                        f"Matrix is missing score for "
                        f"{first!r} and {second!r}."
                    )

                if normalized[(first, second)] != normalized[(second, first)]:
                    raise ValueError(
                        "Substitution matrix must be symmetric."
                    )

        object.__setattr__(
            self,
            "scores",
            MappingProxyType(normalized),
        )

    @property
    def residues(self) -> tuple[str, ...]:
        """Return the residue symbols supported by this matrix."""
        return tuple(sorted({
            residue
            for pair in self.scores
            for residue in pair
        }))

    def score(self, first: str, second: str) -> float:
        """Return the substitution score for a residue pair."""
        self.alphabet.validate_residues(first)
        self.alphabet.validate_residues(second)

        if len(first) != 1 or len(second) != 1:
            raise ValueError(
                "Matrix scoring requires exactly one residue per input."
            )

        try:
            return self.scores[(first, second)]
        except KeyError:
            raise KeyError(
                f"Matrix {self.name!r} does not support "
                f"the residue pair {first!r}, {second!r}."
            ) from None

    @classmethod
    def from_ncbi_text(
        cls,
        text: str,
        *,
        name: str,
        alphabet: SequenceAlphabet,
    ) -> SubstitutionMatrix:
        """
        Parse a whitespace-delimited NCBI substitution matrix.

        The first non-comment line contains residue symbols.
        Each following data row starts with a residue symbol
        followed by one score per header symbol.
        """
        if not isinstance(text, str):
            raise TypeError("Matrix text must be a string.")

        if not text.strip():
            raise ValueError("Matrix text cannot be empty.")

        if not isinstance(alphabet, SequenceAlphabet):
            raise TypeError(
                "Alphabet must be a SequenceAlphabet instance."
            )

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]

        if not lines:
            raise ValueError("Matrix text contains no data.")

        header = lines[0].split()

        if not header:
            raise ValueError("Matrix header cannot be empty.")

        if len(header) != len(set(header)):
            raise ValueError(
                "Matrix header contains duplicate residue symbols."
            )

        for residue in header:
            alphabet.validate_residues(residue)

            if len(residue) != 1:
                raise ValueError(
                    "Matrix header entries must be single residue symbols."
                )

        scores: dict[tuple[str, str], float] = {}
        seen_rows: set[str] = set()

        for line in lines[1:]:
            parts = line.split()

            if len(parts) != len(header) + 1:
                raise ValueError(
                    "Each matrix row must contain one residue label "
                    "and one score per header symbol."
                )

            row_residue = parts[0]

            if len(row_residue) != 1:
                raise ValueError(
                    "Matrix row labels must be single residue symbols."
                )

            alphabet.validate_residues(row_residue)

            if row_residue not in header:
                raise ValueError(
                    f"Unexpected matrix row residue: {row_residue!r}."
                )

            if row_residue in seen_rows:
                raise ValueError(
                    f"Duplicate matrix row: {row_residue!r}."
                )

            seen_rows.add(row_residue)

            for column_residue, raw_score in zip(header, parts[1:]):
                try:
                    value = float(raw_score)
                except ValueError:
                    raise ValueError(
                        f"Invalid substitution score: {raw_score!r}."
                    ) from None

                scores[(row_residue, column_residue)] = value

        if seen_rows != set(header):
            missing = sorted(set(header) - seen_rows)

            raise ValueError(
                f"Matrix is missing rows for: {', '.join(missing)}."
            )

        return cls(
            name=name,
            alphabet=alphabet,
            scores=scores,
        )


def _build_blosum62() -> SubstitutionMatrix:
    """Build the standard BLOSUM62 matrix for 20 amino acids."""

    residues = "ARNDCQEGHILKMFPSTWYV"

    rows = (
        (4, -1, -2, -2, 0, -1, -1, 0, -2, -1, -1, -1, -1, -2, -1, 1, 0, -3, -2, 0),
        (-1, 5, 0, -2, -3, 1, 0, -2, 0, -3, -2, 2, -1, -3, -2, -1, -1, -3, -2, -3),
        (-2, 0, 6, 1, -3, 0, 0, 0, 1, -3, -3, 0, -2, -3, -2, 1, 0, -4, -2, -3),
        (-2, -2, 1, 6, -3, 0, 2, -1, -1, -3, -4, -1, -3, -3, -1, 0, -1, -4, -3, -3),
        (0, -3, -3, -3, 9, -3, -4, -3, -3, -1, -1, -3, -1, -2, -3, -1, -1, -2, -2, -1),
        (-1, 1, 0, 0, -3, 5, 2, -2, 0, -3, -2, 1, 0, -3, -1, 0, -1, -2, -1, -2),
        (-1, 0, 0, 2, -4, 2, 5, -2, 0, -3, -3, 1, -2, -3, -1, 0, -1, -3, -2, -2),
        (0, -2, 0, -1, -3, -2, -2, 6, -2, -4, -4, -2, -3, -3, -2, 0, -2, -2, -3, -3),
        (-2, 0, 1, -1, -3, 0, 0, -2, 8, -3, -3, -1, -2, -1, -2, -1, -2, -2, 2, -3),
        (-1, -3, -3, -3, -1, -3, -3, -4, -3, 4, 2, -3, 1, 0, -3, -2, -1, -3, -1, 3),
        (-1, -2, -3, -4, -1, -2, -3, -4, -3, 2, 4, -2, 2, 0, -3, -2, -1, -2, -1, 1),
        (-1, 2, 0, -1, -3, 1, 1, -2, -1, -3, -2, 5, -1, -3, -1, 0, -1, -3, -2, -2),
        (-1, -1, -2, -3, -1, 0, -2, -3, -2, 1, 2, -1, 5, 0, -2, -1, -1, -1, -1, 1),
        (-2, -3, -3, -3, -2, -3, -3, -3, -1, 0, 0, -3, 0, 6, -4, -2, -2, 1, 3, -1),
        (-1, -2, -2, -1, -3, -1, -1, -2, -2, -3, -3, -1, -2, -4, 7, -1, -1, -4, -3, -2),
        (1, -1, 1, 0, -1, 0, 0, 0, -1, -2, -2, 0, -1, -2, -1, 4, 1, -3, -2, -2),
        (0, -1, 0, -1, -1, -1, -1, -2, -2, -1, -1, -1, -1, -2, -1, 1, 5, -2, -2, 0),
        (-3, -3, -4, -4, -2, -2, -3, -2, -2, -3, -2, -3, -1, 1, -4, -3, -2, 11, 2, -3),
        (-2, -2, -2, -3, -2, -1, -2, -3, 2, -1, -1, -2, -1, 3, -3, -2, -2, 2, 7, -1),
        (0, -3, -3, -3, -1, -2, -2, -3, -3, 3, 1, -2, 1, -1, -2, -2, 0, -3, -1, 4),
    )

    scores = {
        (first, second): rows[i][j]
        for i, first in enumerate(residues)
        for j, second in enumerate(residues)
    }

    return SubstitutionMatrix(
        name="BLOSUM62",
        alphabet=SequenceAlphabet.PROTEIN,
        scores=scores,
    )


BLOSUM62 = _build_blosum62()
