
from aditi.data.normalization.sbml import SBMLPathwayConverter
from aditi.data.parsers.sbml import SBMLParser
from aditi.domain.pathways.pathway import Pathway


class SBMLImportService:
    """
    Coordinate SBML parsing and domain conversion.

    The service owns the import workflow but delegates XML
    interpretation and domain construction to their respective
    components.
    """

    def __init__(
        self,
        parser: SBMLParser | None = None,
        converter: SBMLPathwayConverter | None = None,
    ) -> None:
        if parser is not None and not isinstance(parser, SBMLParser):
            raise TypeError(
                "parser must be an SBMLParser instance."
            )

        if converter is not None and not isinstance(
            converter,
            SBMLPathwayConverter,
        ):
            raise TypeError(
                "converter must be an SBMLPathwayConverter instance."
            )

        self._parser = parser if parser is not None else SBMLParser()
        self._converter = (
            converter
            if converter is not None
            else SBMLPathwayConverter()
        )

    def import_pathway(self, source: str | bytes) -> Pathway:
        """
        Import an SBML document into an Aditi domain Pathway.

        Args:
            source: SBML XML document as a string or bytes.

        Returns:
            A fully constructed domain Pathway.

        Raises:
            TypeError: If the source has an unsupported type.
            SBMLParseError: If the SBML document is invalid.
            SBMLConversionError: If domain conversion fails.
        """

        if not isinstance(source, (str, bytes)):
            raise TypeError(
                "SBML source must be a string or bytes."
            )

        parsed_pathway = self._parser.parse(source)

        return self._converter.convert(parsed_pathway)
