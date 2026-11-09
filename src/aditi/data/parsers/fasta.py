
from __future__ import annotations

from dataclasses import dataclass


class FastaParseError(ValueError):
    """Raised when a FASTA document cannot be parsed."""


@dataclass(frozen=True, slots=True)
class ParsedFastaRecord:
    """A sequence record extracted from a FASTA document."""

    identifier: str
    description: str | None
    residues: str


class FastaParser:
    """
    Parse FASTA-formatted text into neutral sequence records.

    Supports:
    - Multiple FASTA records.
    - Multiline sequences.
    - Optional descriptions in headers.
    - Whitespace between sequence fragments.

    Alphabet validation is intentionally delegated to the
    domain layer.
    """

    def parse(self, source: str | bytes) -> tuple[ParsedFastaRecord, ...]:
        """
        Parse a FASTA document.

        Args:
            source: FASTA document as a string or UTF-8 bytes.

        Returns:
            An ordered tuple of parsed FASTA records.

        Raises:
            TypeError: If source has an unsupported type.
            FastaParseError: If the document is malformed.
        """

        if not isinstance(source, (str, bytes)):
            raise TypeError(
                "FASTA source must be a string or bytes."
            )

        if isinstance(source, bytes):
            try:
                source = source.decode("utf-8")
            except UnicodeDecodeError as error:
                raise FastaParseError(
                    "FASTA document must contain valid UTF-8 text."
                ) from error

        if not source or not source.strip():
            raise FastaParseError(
                "FASTA document cannot be empty."
            )

        records: list[ParsedFastaRecord] = []

        current_identifier: str | None = None
        current_description: str | None = None
        current_fragments: list[str] = []

        def finish_record() -> None:
            if current_identifier is None:
                return

            residues = "".join(current_fragments)

            if not residues:
                raise FastaParseError(
                    f"FASTA record '{current_identifier}' "
                    "does not contain any sequence residues."
                )

            records.append(
                ParsedFastaRecord(
                    identifier=current_identifier,
                    description=current_description,
                    residues=residues,
                )
            )

        for line_number, raw_line in enumerate(
            source.splitlines(),
            start=1,
        ):
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith(">"):
                finish_record()

                header = line[1:].strip()

                if not header:
                    raise FastaParseError(
                        f"FASTA header on line {line_number} is empty."
                    )

                parts = header.split(maxsplit=1)

                current_identifier = parts[0]
                current_description = (
                    parts[1]
                    if len(parts) > 1
                    else None
                )

                current_fragments = []
                continue

            if current_identifier is None:
                raise FastaParseError(
                    f"Sequence data encountered before the first "
                    f"FASTA header on line {line_number}."
                )

            if any(character.isspace() for character in line):
                fragments = line.split()
            else:
                fragments = [line]

            current_fragments.extend(fragments)

        finish_record()

        if not records:
            raise FastaParseError(
                "FASTA document does not contain any records."
            )

        identifiers = [
            record.identifier
            for record in records
        ]

        if len(identifiers) != len(set(identifiers)):
            raise FastaParseError(
                "FASTA document contains duplicate record identifiers."
            )

        return tuple(records)
