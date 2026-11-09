
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class SBMLParseError(ValueError):
    """Raised when an SBML document cannot be parsed."""


@dataclass(frozen=True, slots=True)
class ParsedMetabolite:
    """A metabolite extracted from an SBML species."""

    identifier: str
    name: str
    chemical_formula: str | None = None
    charge: int | None = None


@dataclass(frozen=True, slots=True)
class ParsedReactionParticipant:
    """A species reference within an SBML reaction."""

    metabolite_identifier: str
    coefficient: Decimal = Decimal(1)


@dataclass(frozen=True, slots=True)
class ParsedReaction:
    """A reaction extracted from an SBML model."""

    identifier: str
    name: str
    reactants: tuple[ParsedReactionParticipant, ...]
    products: tuple[ParsedReactionParticipant, ...]
    reversible: bool


@dataclass(frozen=True, slots=True)
class ParsedPathway:
    """A neutral, parser-independent pathway representation."""

    identifier: str | None
    name: str
    metabolites: tuple[ParsedMetabolite, ...]
    reactions: tuple[ParsedReaction, ...]


class SBMLParser:
    """
    Parse core SBML XML into Aditi's neutral pathway representation.

    The parser supports SBML core model, species, reaction,
    speciesReference, stoichiometry, and reversible attributes.
    """

    _XML_DECLARATION_PATTERN = re.compile(
        r"<!\s*(?:DOCTYPE|ENTITY)\b",
        re.IGNORECASE,
    )

    @staticmethod
    def _local_name(tag: str) -> str:
        """Return an XML tag without its namespace."""

        if "}" in tag:
            return tag.rsplit("}", 1)[1]

        return tag

    @classmethod
    def _find_child(
        cls,
        element: ET.Element,
        name: str,
    ) -> ET.Element | None:
        """Find a direct child by its local XML name."""

        for child in element:
            if cls._local_name(child.tag) == name:
                return child

        return None

    @classmethod
    def _find_children(
        cls,
        element: ET.Element,
        name: str,
    ) -> tuple[ET.Element, ...]:
        """Find direct children by their local XML name."""

        return tuple(
            child
            for child in element
            if cls._local_name(child.tag) == name
        )

    @staticmethod
    def _required_attribute(
        element: ET.Element,
        attribute: str,
        context: str,
    ) -> str:
        """Read a required, non-empty XML attribute."""

        value = element.get(attribute)

        if value is None or not value.strip():
            raise SBMLParseError(
                f"{context} requires a non-empty '{attribute}' attribute."
            )

        return value

    @staticmethod
    def _parse_reversible(value: str | None, reaction_id: str) -> bool:
        """Parse an SBML boolean attribute."""

        if value is None:
            return True

        normalized = value.strip().lower()

        if normalized in {"true", "1"}:
            return True

        if normalized in {"false", "0"}:
            return False

        raise SBMLParseError(
            f"Reaction '{reaction_id}' has invalid reversible value '{value}'."
        )

    @staticmethod
    def _parse_charge(
        value: str | None,
        species_id: str,
    ) -> int | None:
        """Parse an optional integer charge."""

        if value is None:
            return None

        try:
            return int(value)
        except ValueError as error:
            raise SBMLParseError(
                f"Species '{species_id}' has an invalid charge."
            ) from error

    @staticmethod
    def _parse_stoichiometry(
        value: str | None,
        reaction_id: str,
        species_id: str,
    ) -> Decimal:
        """Parse a positive finite stoichiometric coefficient."""

        if value is None:
            return Decimal(1)

        try:
            coefficient = Decimal(value)
        except InvalidOperation as error:
            raise SBMLParseError(
                f"Reaction '{reaction_id}' has invalid stoichiometry "
                f"for species '{species_id}'."
            ) from error

        if not coefficient.is_finite() or coefficient <= 0:
            raise SBMLParseError(
                f"Reaction '{reaction_id}' requires positive finite "
                f"stoichiometry for species '{species_id}'."
            )

        return coefficient

    def parse(self, source: str | bytes) -> ParsedPathway:
        """
        Parse an SBML XML document.

        Args:
            source: XML document as a string or bytes.

        Returns:
            A ParsedPathway containing metabolites and reactions.

        Raises:
            SBMLParseError: If the document is malformed or contains
                unsupported or invalid core pathway structures.
        """

        if not isinstance(source, (str, bytes)):
            raise TypeError("SBML source must be a string or bytes.")

        if not source:
            raise SBMLParseError("SBML document cannot be empty.")

        if isinstance(source, bytes):
            inspection_text = source.decode("utf-8", errors="ignore")
        else:
            inspection_text = source

        if self._XML_DECLARATION_PATTERN.search(inspection_text):
            raise SBMLParseError(
                "DOCTYPE and ENTITY declarations are not supported."
            )

        try:
            root = ET.fromstring(source)
        except ET.ParseError as error:
            raise SBMLParseError(
                f"Invalid SBML XML document: {error}."
            ) from error

        if self._local_name(root.tag) != "sbml":
            raise SBMLParseError(
                "The XML document root must be an SBML element."
            )

        model = self._find_child(root, "model")

        if model is None:
            raise SBMLParseError(
                "The SBML document does not contain a model."
            )

        return self._parse_model(model)

    def _parse_model(self, model: ET.Element) -> ParsedPathway:
        """Extract pathway data from an SBML model."""

        model_id = model.get("id")
        model_name = model.get("name")

        pathway_name = (
            model_name.strip()
            if model_name and model_name.strip()
            else model_id.strip()
            if model_id and model_id.strip()
            else "Unnamed pathway"
        )

        list_of_species = self._find_child(
            model,
            "listOfSpecies",
        )

        if list_of_species is None:
            raise SBMLParseError(
                "The SBML model does not contain listOfSpecies."
            )

        metabolites: list[ParsedMetabolite] = []
        metabolite_ids: set[str] = set()

        for species in self._find_children(
            list_of_species,
            "species",
        ):
            species_id = self._required_attribute(
                species,
                "id",
                "SBML species",
            )

            if species_id in metabolite_ids:
                raise SBMLParseError(
                    f"Duplicate SBML species identifier '{species_id}'."
                )

            metabolite_ids.add(species_id)

            species_name = species.get("name")
            name = (
                species_name.strip()
                if species_name and species_name.strip()
                else species_id
            )

            metabolites.append(
                ParsedMetabolite(
                    identifier=species_id,
                    name=name,
                    charge=self._parse_charge(
                        species.get("charge"),
                        species_id,
                    ),
                )
            )

        list_of_reactions = self._find_child(
            model,
            "listOfReactions",
        )

        if list_of_reactions is None:
            raise SBMLParseError(
                "The SBML model does not contain listOfReactions."
            )

        reactions: list[ParsedReaction] = []
        reaction_ids: set[str] = set()

        for reaction in self._find_children(
            list_of_reactions,
            "reaction",
        ):
            parsed_reaction = self._parse_reaction(
                reaction,
                metabolite_ids,
            )

            if parsed_reaction.identifier in reaction_ids:
                raise SBMLParseError(
                    "Duplicate SBML reaction identifier "
                    f"'{parsed_reaction.identifier}'."
                )

            reaction_ids.add(parsed_reaction.identifier)
            reactions.append(parsed_reaction)

        if not metabolites:
            raise SBMLParseError(
                "The SBML model contains no species."
            )

        if not reactions:
            raise SBMLParseError(
                "The SBML model contains no reactions."
            )

        return ParsedPathway(
            identifier=model_id,
            name=pathway_name,
            metabolites=tuple(metabolites),
            reactions=tuple(reactions),
        )

    def _parse_reaction(
        self,
        reaction: ET.Element,
        known_metabolites: set[str],
    ) -> ParsedReaction:
        """Parse a single SBML reaction."""

        reaction_id = self._required_attribute(
            reaction,
            "id",
            "SBML reaction",
        )

        reaction_name = reaction.get("name")
        name = (
            reaction_name.strip()
            if reaction_name and reaction_name.strip()
            else reaction_id
        )

        if self._find_child(reaction, "listOfModifiers") is not None:
            raise SBMLParseError(
                f"Reaction '{reaction_id}' contains modifier species "
                "references, which are not supported yet."
            )

        reactants = self._parse_participants(
            reaction,
            "listOfReactants",
            "speciesReference",
            reaction_id,
            known_metabolites,
        )

        products = self._parse_participants(
            reaction,
            "listOfProducts",
            "speciesReference",
            reaction_id,
            known_metabolites,
        )

        if not reactants or not products:
            raise SBMLParseError(
                f"Reaction '{reaction_id}' must contain at least "
                "one reactant and one product."
            )

        return ParsedReaction(
            identifier=reaction_id,
            name=name,
            reactants=reactants,
            products=products,
            reversible=self._parse_reversible(
                reaction.get("reversible"),
                reaction_id,
            ),
        )

    def _parse_participants(
        self,
        reaction: ET.Element,
        list_name: str,
        reference_name: str,
        reaction_id: str,
        known_metabolites: set[str],
    ) -> tuple[ParsedReactionParticipant, ...]:
        """Parse reactant or product species references."""

        participant_list = self._find_child(
            reaction,
            list_name,
        )

        if participant_list is None:
            return ()

        participants: list[ParsedReactionParticipant] = []
        seen_species: set[str] = set()

        for reference in self._find_children(
            participant_list,
            reference_name,
        ):
            species_id = self._required_attribute(
                reference,
                "species",
                f"Reaction '{reaction_id}' species reference",
            )

            if species_id not in known_metabolites:
                raise SBMLParseError(
                    f"Reaction '{reaction_id}' references unknown "
                    f"species '{species_id}'."
                )

            if species_id in seen_species:
                raise SBMLParseError(
                    f"Reaction '{reaction_id}' contains duplicate "
                    f"species reference '{species_id}'."
                )

            seen_species.add(species_id)

            coefficient = self._parse_stoichiometry(
                reference.get("stoichiometry"),
                reaction_id,
                species_id,
            )

            participants.append(
                ParsedReactionParticipant(
                    metabolite_identifier=species_id,
                    coefficient=coefficient,
                )
            )

        return tuple(participants)
