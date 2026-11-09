
from __future__ import annotations

from dataclasses import dataclass

from aditi.domain.entities.base import BiologicalEntity
from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.pathways.metabolite import Metabolite
from aditi.domain.pathways.reaction import Reaction


@dataclass(frozen=True, slots=True, kw_only=True)
class Pathway(BiologicalEntity):
    """
    Represents a biological pathway composed of biochemical reactions.

    The pathway owns an ordered collection of reactions.
    Its metabolites are derived from the reaction participants.
    """

    name: str
    reactions: tuple[Reaction, ...]
    description: str | None = None

    def __post_init__(self) -> None:
        BiologicalEntity.__post_init__(self)

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError(
                "Pathway name must be a non-empty string."
            )

        if self.name != self.name.strip():
            raise ValueError(
                "Pathway name cannot contain leading or trailing whitespace."
            )

        if (
            self.description is not None
            and (
                not isinstance(self.description, str)
                or not self.description.strip()
            )
        ):
            raise ValueError(
                "Pathway description must be a non-empty string when provided."
            )

        if (
            self.description is not None
            and self.description != self.description.strip()
        ):
            raise ValueError(
                "Pathway description cannot contain leading or trailing whitespace."
            )

        if not isinstance(self.reactions, tuple):
            raise TypeError(
                "Pathway reactions must be provided as a tuple."
            )

        if not self.reactions:
            raise ValueError(
                "A pathway must contain at least one reaction."
            )

        seen_reactions: set[EntityIdentity] = set()

        for reaction in self.reactions:
            if not isinstance(reaction, Reaction):
                raise TypeError(
                    "All pathway reactions must be Reaction instances."
                )

            if reaction.identity in seen_reactions:
                raise ValueError(
                    "Pathway cannot contain duplicate reactions."
                )

            seen_reactions.add(reaction.identity)

    @property
    def metabolites(self) -> tuple[Metabolite, ...]:
        """
        Return unique metabolites referenced by pathway reactions.

        Metabolites are ordered by their first appearance while
        traversing reactions, reactants, and then products.
        """

        metabolites: list[Metabolite] = []
        seen_identities: set[EntityIdentity] = set()

        for reaction in self.reactions:
            participants = (
                *reaction.reactants,
                *reaction.products,
            )

            for participant in participants:
                metabolite = participant.metabolite
                identity = metabolite.identity

                if identity in seen_identities:
                    continue

                seen_identities.add(identity)
                metabolites.append(metabolite)

        return tuple(metabolites)

    @property
    def entity_type(self) -> str:
        """Return the biological entity type."""
        return "pathway"
