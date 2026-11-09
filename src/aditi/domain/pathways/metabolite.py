
from __future__ import annotations

from dataclasses import dataclass

from aditi.domain.entities.base import BiologicalEntity


@dataclass(frozen=True, slots=True, kw_only=True)
class Metabolite(BiologicalEntity):
    """
    Represents a chemical metabolite in a biological pathway.

    A metabolite has a biological identity, external database
    references, a name, and optional chemical properties.
    """

    name: str
    chemical_formula: str | None = None
    charge: int | None = None

    def __post_init__(self) -> None:
        BiologicalEntity.__post_init__(self)

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError(
                "Metabolite name must be a non-empty string."
            )

        if self.name != self.name.strip():
            raise ValueError(
                "Metabolite name cannot contain leading or trailing whitespace."
            )

        if self.chemical_formula is not None:
            if (
                not isinstance(self.chemical_formula, str)
                or not self.chemical_formula.strip()
            ):
                raise ValueError(
                    "Chemical formula must be a non-empty string when provided."
                )

            if self.chemical_formula != self.chemical_formula.strip():
                raise ValueError(
                    "Chemical formula cannot contain leading or trailing whitespace."
                )

        if (
            self.charge is not None
            and (
                isinstance(self.charge, bool)
                or not isinstance(self.charge, int)
            )
        ):
            raise TypeError(
                "Metabolite charge must be an integer when provided."
            )

    @property
    def entity_type(self) -> str:
        """Return the biological entity type."""
        return "metabolite"
