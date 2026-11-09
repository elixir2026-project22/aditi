
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PathwayRequestModel(BaseModel):
    """Base configuration for pathway request models."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class MetaboliteRequest(PathwayRequestModel):
    """Input definition for a pathway metabolite."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    chemical_formula: str | None = None
    charge: int | None = None


class ReactionParticipantRequest(PathwayRequestModel):
    """Reference to a metabolite participating in a reaction."""

    metabolite_id: str = Field(min_length=1)
    coefficient: Decimal = Field(
        default=Decimal(1),
        gt=0,
        allow_inf_nan=False,
    )


class ReactionRequest(PathwayRequestModel):
    """Input definition for a biochemical reaction."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    reactants: tuple[ReactionParticipantRequest, ...] = Field(
        min_length=1
    )
    products: tuple[ReactionParticipantRequest, ...] = Field(
        min_length=1
    )
    reversible: bool = False

    @model_validator(mode="after")
    def validate_participants(self) -> ReactionRequest:
        """Reject repeated metabolite references on either side."""

        for side_name, participants in (
            ("reactants", self.reactants),
            ("products", self.products),
        ):
            identifiers = [
                participant.metabolite_id
                for participant in participants
            ]

            if len(identifiers) != len(set(identifiers)):
                raise ValueError(
                    f"Reaction {side_name} cannot contain "
                    "duplicate metabolite references."
                )

        return self


class PathwayDefinitionRequest(PathwayRequestModel):
    """
    Complete pathway definition accepted by the API.

    Reactions reference metabolites using request-local identifiers.
    These identifiers are used only during graph construction and are
    not substituted for Aditi's internal biological entity identities.
    """

    name: str = Field(min_length=1)
    description: str | None = None
    metabolites: tuple[MetaboliteRequest, ...] = Field(
        min_length=1
    )
    reactions: tuple[ReactionRequest, ...] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validate_references(self) -> PathwayDefinitionRequest:
        """Validate unique identifiers and participant references."""

        metabolite_ids = [
            metabolite.id
            for metabolite in self.metabolites
        ]

        if len(metabolite_ids) != len(set(metabolite_ids)):
            raise ValueError(
                "Pathway metabolite identifiers must be unique."
            )

        reaction_ids = [
            reaction.id
            for reaction in self.reactions
        ]

        if len(reaction_ids) != len(set(reaction_ids)):
            raise ValueError(
                "Pathway reaction identifiers must be unique."
            )

        known_metabolites = set(metabolite_ids)

        for reaction in self.reactions:
            for participant in (
                *reaction.reactants,
                *reaction.products,
            ):
                if participant.metabolite_id not in known_metabolites:
                    raise ValueError(
                        f"Reaction '{reaction.id}' references "
                        f"unknown metabolite "
                        f"'{participant.metabolite_id}'."
                    )

        return self
