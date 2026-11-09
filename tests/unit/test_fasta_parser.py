
import pytest

from aditi.data.parsers.fasta import (
    FastaParseError,
    FastaParser,
    ParsedFastaRecord,
)


@pytest.fixture
def parser() -> FastaParser:
    return FastaParser()


def test_parse_single_fasta_record(parser: FastaParser) -> None:
    source = ">seq1 Human gene\nATGCGT"

    records = parser.parse(source)

    assert len(records) == 1
    assert records[0] == ParsedFastaRecord(
        identifier="seq1",
        description="Human gene",
        residues="ATGCGT",
    )


def test_parse_multiple_fasta_records(parser: FastaParser) -> None:
    source = (
        ">seq1 First sequence\n"
        "ATGC\n"
        ">seq2 Second sequence\n"
        "AUGC\n"
    )

    records = parser.parse(source)

    assert len(records) == 2
    assert records[0].identifier == "seq1"
    assert records[1].identifier == "seq2"


def test_parse_multiline_sequence(parser: FastaParser) -> None:
    source = ">seq1\nATGC\nGTAA\nCCGG"

    records = parser.parse(source)

    assert records[0].residues == "ATGCGTAACCGG"


def test_parse_header_without_description(parser: FastaParser) -> None:
    source = ">seq1\nATGC"

    records = parser.parse(source)

    assert records[0].identifier == "seq1"
    assert records[0].description is None


def test_parse_header_with_description(parser: FastaParser) -> None:
    source = ">seq1 Homo sapiens gene\nATGC"

    records = parser.parse(source)

    assert records[0].description == "Homo sapiens gene"


def test_parse_preserves_sequence_case(parser: FastaParser) -> None:
    source = ">seq1\natgc"

    records = parser.parse(source)

    assert records[0].residues == "atgc"


def test_parse_ignores_blank_lines(parser: FastaParser) -> None:
    source = (
        "\n"
        ">seq1\n"
        "\n"
        "ATGC\n"
        "\n"
        "GTAA\n"
        "\n"
    )

    records = parser.parse(source)

    assert len(records) == 1
    assert records[0].residues == "ATGCGTAA"


def test_parse_sequence_with_internal_whitespace(
    parser: FastaParser,
) -> None:
    source = ">seq1\nATGC GTAA"

    records = parser.parse(source)

    assert records[0].residues == "ATGCGTAA"


def test_parse_utf8_bytes(parser: FastaParser) -> None:
    source = ">seq1 Human gene\nATGC".encode("utf-8")

    records = parser.parse(source)

    assert records[0].identifier == "seq1"
    assert records[0].residues == "ATGC"


def test_parse_returns_tuple(parser: FastaParser) -> None:
    records = parser.parse(">seq1\nATGC")

    assert isinstance(records, tuple)


def test_parse_rejects_empty_document(parser: FastaParser) -> None:
    with pytest.raises(FastaParseError):
        parser.parse("")


def test_parse_rejects_whitespace_document(
    parser: FastaParser,
) -> None:
    with pytest.raises(FastaParseError):
        parser.parse("   \n  \n")


def test_parse_rejects_sequence_before_header(
    parser: FastaParser,
) -> None:
    with pytest.raises(FastaParseError):
        parser.parse("ATGC\n>seq1")


def test_parse_rejects_empty_header(parser: FastaParser) -> None:
    with pytest.raises(FastaParseError):
        parser.parse(">\nATGC")


def test_parse_rejects_empty_record(parser: FastaParser) -> None:
    source = ">seq1\n>seq2\nATGC"

    with pytest.raises(FastaParseError):
        parser.parse(source)


def test_parse_rejects_duplicate_identifiers(
    parser: FastaParser,
) -> None:
    source = ">seq1 First\nATGC\n>seq1 Second\nGTAA"

    with pytest.raises(FastaParseError):
        parser.parse(source)


def test_parse_rejects_invalid_utf8(parser: FastaParser) -> None:
    with pytest.raises(FastaParseError):
        parser.parse(b"\xff\xfe\xfa")


def test_parse_rejects_unsupported_source_type(
    parser: FastaParser,
) -> None:
    with pytest.raises(TypeError):
        parser.parse(123)  # type: ignore[arg-type]
