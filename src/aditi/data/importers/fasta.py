
from aditi.data.parsers.fasta import FastaParser
from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.domain.sequences.biological_sequence import BiologicalSequence


class FastaImportService:
    """
    Coordinate FASTA parsing and biological sequence construction.

    The service delegates FASTA interpretation to FastaParser
    and constructs validated BiologicalSequence domain objects.
    """

    def __init__(
        self,
        parser: FastaParser | None = None,
    ) -> None:
        if parser is not None and not isinstance(parser, FastaParser):
            raise TypeError(
                "parser must be a FastaParser instance."
            )

        self._parser = (
            parser if parser is not None else FastaParser()
        )

    def import_sequences(
        self,
        source: str | bytes,
        alphabet: SequenceAlphabet,
    ) -> tuple[BiologicalSequence, ...]:
        """
        Import FASTA records into biological sequence objects.

        Args:
            source: FASTA document as a string or bytes.
            alphabet: Explicit biological sequence alphabet.

        Returns:
            An ordered tuple of BiologicalSequence objects.

        Raises:
            TypeError: If source or alphabet has an unsupported type.
            FastaParseError: If the FASTA document is invalid.
            ValueError: If a sequence violates its alphabet.
        """

        if not isinstance(source, (str, bytes)):
            raise TypeError(
                "FASTA source must be a string or bytes."
            )

        if not isinstance(alphabet, SequenceAlphabet):
            raise TypeError(
                "alphabet must be a SequenceAlphabet instance."
            )

        parsed_records = self._parser.parse(source)

        sequences: list[BiologicalSequence] = []

        for record in parsed_records:
            try:
                sequence = BiologicalSequence(
                    name=record.identifier,
                    residues=record.residues,
                    alphabet=alphabet,
                    description=record.description,
                )
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Failed to import FASTA record "
                    f"'{record.identifier}': {error}"
                ) from error

            sequences.append(sequence)

        return tuple(sequences)
