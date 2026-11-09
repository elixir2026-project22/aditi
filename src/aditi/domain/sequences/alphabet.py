
from __future__ import annotations

from enum import Enum


class SequenceAlphabet(str, Enum):
    """
    Defines the supported biological sequence alphabets.

    DNA and RNA support ambiguous nucleotide N.
    Protein supports standard amino acids and commonly
    used ambiguity or special amino acid codes.
    """

    DNA = "dna"
    RNA = "rna"
    PROTEIN = "protein"

    @property
    def allowed_residues(self) -> frozenset[str]:
        """Return the valid residue symbols for this alphabet."""

        if self is SequenceAlphabet.DNA:
            return frozenset("ACGTN")

        if self is SequenceAlphabet.RNA:
            return frozenset("ACGUN")

        if self is SequenceAlphabet.PROTEIN:
            return frozenset(
                "ACDEFGHIKLMNPQRSTVWY"
                "BZJXUO"
            )

        raise ValueError(
            f"Unsupported sequence alphabet: {self!r}"
        )

    def validate_residues(self, residues: str) -> None:
        """
        Validate a normalized, uppercase biological sequence.

        Whitespace and alignment gaps are intentionally rejected.
        FASTA parsing and alignment processing handle those concerns
        at their respective layers.
        """

        if not isinstance(residues, str):
            raise TypeError(
                "Sequence residues must be provided as a string."
            )

        if not residues:
            raise ValueError(
                "Sequence residues cannot be empty."
            )

        if residues != residues.upper():
            raise ValueError(
                "Sequence residues must contain uppercase symbols."
            )

        allowed = self.allowed_residues

        invalid_residues = sorted(
            set(residues) - allowed
        )

        if invalid_residues:
            invalid_symbols = ", ".join(
                repr(symbol)
                for symbol in invalid_residues
            )

            raise ValueError(
                f"Invalid residues for {self.value} alphabet: "
                f"{invalid_symbols}."
            )
