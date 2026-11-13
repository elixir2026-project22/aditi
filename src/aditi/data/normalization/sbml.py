
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

    Repeated modifier references are retained by the parser but
    represented once per metabolite in the domain reaction.
    """

    NAMESPACE = "sbml"

    @staticmethod
    def _validate_identifier(identifier: str, context: str) -> None:
        if not isinstance(identifier, str) or not identifier.strip():
            raise SBMLConversionError(
                f"{context} requires a non-empty identifier."
            )

    def _convert_participants(
        self,
        participants,
        metabolites: dict[str, Metabolite],
        reaction_identifier: str,
        *,
        unique_metabolites: bool = False,
    ) -> tuple[ReactionParticipant, ...]:
        converted: list[ReactionParticipant] = []
        seen_metabolites: set[str] = set()

        for participant in participants:
            metabolite_identifier = participant.metabolite_identifier

            if (
                unique_metabolites
                and metabolite_identifier in seen_metabolites
            ):
                continue

            try:
                metabolite = metabolites[metabolite_identifier]
            except KeyError as error:
                raise SBMLConversionError(
                    f"Reaction '{reaction_identifier}' references unknown "
                    f"metabolite '{metabolite_identifier}'."
                ) from error

            converted.append(
                ReactionParticipant(
                    metabolite=metabolite,
                    coefficient=participant.coefficient,
                )
            )

            seen_metabolites.add(metabolite_identifier)

        return tuple(converted)

    def convert(self, parsed_pathway: ParsedPathway) -> Pathway:
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

            reactants = self._convert_participants(
                parsed_reaction.reactants,
                metabolites,
                identifier,
            )

            products = self._convert_participants(
                parsed_reaction.products,
                metabolites,
                identifier,
            )

            modifiers = self._convert_participants(
                parsed_reaction.modifiers,
                metabolites,
                identifier,
                unique_metabolites=True,
            )

            reactions.append(
                Reaction(
                    name=parsed_reaction.name,
                    reactants=reactants,
                    products=products,
                    modifiers=modifiers,
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
