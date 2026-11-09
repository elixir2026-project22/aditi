
from __future__ import annotations

from dataclasses import dataclass

from aditi.domain.entities.base import BiologicalEntity
from aditi.domain.sequences.alphabet import SequenceAlphabet


@dataclass(frozen=True, slots=True, kw_only=True)
class BiologicalSequence(BiologicalEntity):
    """
    Represents a biological sequence.

    A sequence contains normalized biological residues and
    declares the alphabet used to interpret those residues.

    Supported alphabets:
    - DNA
    - RNA
    - Protein
    """

    name: str
    residues: str
    alphabet: SequenceAlphabet
    description: str | None = None

    def __post_init__(self) -> None:
        BiologicalEntity.__post_init__(self)

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError(
                "Sequence name must be a non-empty string."
            )

        if self.name != self.name.strip():
            raise ValueError(
                "Sequence name cannot contain leading or trailing whitespace."
            )

        if not isinstance(self.alphabet, SequenceAlphabet):
            raise TypeError(
                "Sequence alphabet must be a SequenceAlphabet instance."
            )

        if (
            self.description is not None
            and (
                not isinstance(self.description, str)
                or not self.description.strip()
            )
        ):
            raise ValueError(
                "Sequence description must be a non-empty string when provided."
            )

        if (
            self.description is not None
            and self.description != self.description.strip()
        ):
            raise ValueError(
                "Sequence description cannot contain leading or trailing whitespace."
            )

        self.alphabet.validate_residues(self.residues)

    @property
    def length(self) -> int:
        """Return the number of residues in the sequence."""
        return len(self.residues)

    @property
    def entity_type(self) -> str:
        """Return the biological entity type."""
        return "sequence"
