
from aditi.data.parsers.sbml import ParsedPathway
from aditi.domain.entities.identifiers import ExternalIdentifier
from aditi.domain.pathways.metabolite import Metabolite
from aditi.domain.pathways.pathway import Pathway
from aditi.domain.pathways.reaction import (
    Reaction,
    ReactionParticipant,
)


class SBMLConversionError(ValueError):
    """Raised when parsed SBML data cannot become a domain pathway."""


class SBMLPathwayConverter:
    """
    Convert neutral SBML parser output into Aditi domain entities.

    SBML identifiers are preserved as external identifiers.
    Aditi generates independent internal UUID identities.
    """

    NAMESPACE = "sbml"

    @staticmethod
    def _validate_identifier(identifier: str, context: str) -> None:
        if not isinstance(identifier, str) or not identifier.strip():
            raise SBMLConversionError(
                f"{context} requires a non-empty identifier."
            )

    def convert(self, parsed_pathway: ParsedPathway) -> Pathway:
        """Convert a parsed SBML pathway into a domain Pathway."""

        if not isinstance(parsed_pathway, ParsedPathway):
            raise TypeError(
                "SBML conversion requires a ParsedPathway instance."
            )

        metabolites: dict[str, Metabolite] = {}

        for parsed_metabolite in parsed_pathway.metabolites:
            identifier = parsed_metabolite.identifier

            self._validate_identifier(
                identifier,
                "SBML metabolite",
            )

            if identifier in metabolites:
                raise SBMLConversionError(
                    f"Duplicate SBML metabolite identifier '{identifier}'."
                )

            metabolites[identifier] = Metabolite(
                name=parsed_metabolite.name,
                chemical_formula=parsed_metabolite.chemical_formula,
                charge=parsed_metabolite.charge,
                external_identifiers=(
                    ExternalIdentifier(
                        namespace=self.NAMESPACE,
                        value=identifier,
                    ),
                ),
            )

        reactions: list[Reaction] = []
        reaction_ids: set[str] = set()

        for parsed_reaction in parsed_pathway.reactions:
            identifier = parsed_reaction.identifier

            self._validate_identifier(
                identifier,
                "SBML reaction",
            )

            if identifier in reaction_ids:
                raise SBMLConversionError(
                    f"Duplicate SBML reaction identifier '{identifier}'."
                )

            reaction_ids.add(identifier)

            try:
                reactants = tuple(
                    ReactionParticipant(
                        metabolite=metabolites[
                            participant.metabolite_identifier
                        ],
                        coefficient=participant.coefficient,
                    )
                    for participant in parsed_reaction.reactants
                )

                products = tuple(
                    ReactionParticipant(
                        metabolite=metabolites[
                            participant.metabolite_identifier
                        ],
                        coefficient=participant.coefficient,
                    )
                    for participant in parsed_reaction.products
                )

            except KeyError as error:
                unknown_identifier = error.args[0]

                raise SBMLConversionError(
                    f"Reaction '{identifier}' references unknown "
                    f"metabolite '{unknown_identifier}'."
                ) from error

            reactions.append(
                Reaction(
                    name=parsed_reaction.name,
                    reactants=reactants,
                    products=products,
                    reversible=parsed_reaction.reversible,
                    external_identifiers=(
                        ExternalIdentifier(
                            namespace=self.NAMESPACE,
                            value=identifier,
                        ),
                    ),
                )
            )

        try:
            return Pathway(
                name=parsed_pathway.name,
                reactions=tuple(reactions),
                external_identifiers=(
                    (
                        ExternalIdentifier(
                            namespace=self.NAMESPACE,
                            value=parsed_pathway.identifier,
                        ),
                    )
                    if parsed_pathway.identifier
                    else ()
                ),
            )

        except (TypeError, ValueError) as error:
            raise SBMLConversionError(
                f"Could not construct domain pathway: {error}"
            ) from error
