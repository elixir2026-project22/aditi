
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from aditi.domain.entities.base import BiologicalEntity
from aditi.domain.pathways.metabolite import Metabolite


@dataclass(frozen=True, slots=True)
class ReactionParticipant:
    """
    Represents a metabolite participating in a biochemical reaction.

    The coefficient describes the metabolite's stoichiometric
    contribution to the reaction.
    """

    metabolite: Metabolite
    coefficient: Decimal = Decimal(1)

    def __post_init__(self) -> None:
        if not isinstance(self.metabolite, Metabolite):
            raise TypeError(
                "Reaction participant must reference a Metabolite."
            )

        if not isinstance(self.coefficient, Decimal):
            raise TypeError(
                "Stoichiometric coefficient must be a Decimal."
            )

        if not self.coefficient.is_finite():
            raise ValueError(
                "Stoichiometric coefficient must be finite."
            )

        if self.coefficient <= 0:
            raise ValueError(
                "Stoichiometric coefficient must be greater than zero."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class Reaction(BiologicalEntity):
    """
    Represents a biochemical reaction connecting metabolites.

    Reactants are consumed and products are produced.
    Stoichiometric coefficients describe their proportions.
    """

    name: str

    reactants: tuple[ReactionParticipant, ...]
    products: tuple[ReactionParticipant, ...]

    reversible: bool = False

    def __post_init__(self) -> None:
        BiologicalEntity.__post_init__(self)

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError(
                "Reaction name must be a non-empty string."
            )

        if self.name != self.name.strip():
            raise ValueError(
                "Reaction name cannot contain leading or trailing whitespace."
            )

        if not isinstance(self.reactants, tuple):
            raise TypeError(
                "Reaction reactants must be provided as a tuple."
            )

        if not isinstance(self.products, tuple):
            raise TypeError(
                "Reaction products must be provided as a tuple."
            )

        if not self.reactants:
            raise ValueError(
                "A reaction must contain at least one reactant."
            )

        if not self.products:
            raise ValueError(
                "A reaction must contain at least one product."
            )

        if not isinstance(self.reversible, bool):
            raise TypeError(
                "Reaction reversibility must be a boolean."
            )

        self._validate_participants(
            self.reactants,
            "reactants",
        )

        self._validate_participants(
            self.products,
            "products",
        )

    @staticmethod
    def _validate_participants(
        participants: tuple[ReactionParticipant, ...],
        label: str,
    ) -> None:
        """Validate reaction participants and prevent duplicate metabolites."""

        seen_metabolites = set()

        for participant in participants:
            if not isinstance(participant, ReactionParticipant):
                raise TypeError(
                    f"All reaction {label} must be ReactionParticipant instances."
                )

            identity = participant.metabolite.identity

            if identity in seen_metabolites:
                raise ValueError(
                    f"Reaction {label} cannot contain duplicate metabolites."
                )

            seen_metabolites.add(identity)

    @property
    def entity_type(self) -> str:
        """Return the biological entity type."""
        return "reaction"
