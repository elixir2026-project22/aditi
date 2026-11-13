
import pytest

from aditi.data.importers.fasta import FastaImportService
from aditi.data.parsers.fasta import (
    FastaParseError,
    FastaParser,
)
from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.domain.sequences.biological_sequence import BiologicalSequence


def test_import_single_dna_sequence() -> None:
    service = FastaImportService()

    sequences = service.import_sequences(
        ">gene1 Human gene\nATGCGT",
        SequenceAlphabet.DNA,
    )

    assert len(sequences) == 1

    sequence = sequences[0]

    assert isinstance(sequence, BiologicalSequence)
    assert sequence.name == "gene1"
    assert sequence.description == "Human gene"
    assert sequence.residues == "ATGCGT"
    assert sequence.alphabet is SequenceAlphabet.DNA
    assert sequence.length == 6


def test_import_rna_sequence() -> None:
    service = FastaImportService()

    sequences = service.import_sequences(
        ">rna1 RNA transcript\nAUGCGU",
        SequenceAlphabet.RNA,
    )

    assert sequences[0].residues == "AUGCGU"
    assert sequences[0].alphabet is SequenceAlphabet.RNA


def test_import_protein_sequence() -> None:
    service = FastaImportService()

    sequences = service.import_sequences(
        ">protein1 Example protein\nMKWVTF",
        SequenceAlphabet.PROTEIN,
    )

    assert sequences[0].residues == "MKWVTF"
    assert sequences[0].alphabet is SequenceAlphabet.PROTEIN


def test_import_multiple_sequences() -> None:
    service = FastaImportService()

    source = (
        ">gene1 First gene\n"
        "ATGC\n"
        ">gene2 Second gene\n"
        "GTAA\n"
        ">gene3 Third gene\n"
        "CCGG\n"
    )

    sequences = service.import_sequences(
        source,
        SequenceAlphabet.DNA,
    )

    assert len(sequences) == 3

    assert [sequence.name for sequence in sequences] == [
        "gene1",
        "gene2",
        "gene3",
    ]

    assert [sequence.residues for sequence in sequences] == [
        "ATGC",
        "GTAA",
        "CCGG",
    ]


def test_import_preserves_record_order() -> None:
    service = FastaImportService()

    source = (
        ">third\n"
        "GGG\n"
        ">first\n"
        "AAA\n"
        ">second\n"
        "CCC\n"
    )

    sequences = service.import_sequences(
        source,
        SequenceAlphabet.DNA,
    )

    assert [sequence.name for sequence in sequences] == [
        "third",
        "first",
        "second",
    ]


def test_import_returns_tuple() -> None:
    service = FastaImportService()

    sequences = service.import_sequences(
        ">gene1\nATGC",
        SequenceAlphabet.DNA,
    )

    assert isinstance(sequences, tuple)


def test_import_accepts_bytes_source() -> None:
    service = FastaImportService()

    sequences = service.import_sequences(
        b">gene1\nATGC",
        SequenceAlphabet.DNA,
    )

    assert sequences[0].residues == "ATGC"


@pytest.mark.parametrize(
    ("alphabet", "residues"),
    [
        (SequenceAlphabet.DNA, "ATUG"),
        (SequenceAlphabet.RNA, "ATCG"),
        (SequenceAlphabet.PROTEIN, "MKW*"),
    ],
)
def test_import_rejects_invalid_residues(
    alphabet: SequenceAlphabet,
    residues: str,
) -> None:
    service = FastaImportService()

    with pytest.raises(ValueError, match="Failed to import FASTA record"):
        service.import_sequences(
            f">invalid_sequence\n{residues}",
            alphabet,
        )


def test_import_rejects_invalid_fasta_document() -> None:
    service = FastaImportService()

    with pytest.raises(FastaParseError):
        service.import_sequences(
            "ATGC\n>gene1",
            SequenceAlphabet.DNA,
        )


def test_import_rejects_invalid_source_type() -> None:
    service = FastaImportService()

    with pytest.raises(TypeError):
        service.import_sequences(
            123,  # type: ignore[arg-type]
            SequenceAlphabet.DNA,
        )


def test_import_rejects_invalid_alphabet_type() -> None:
    service = FastaImportService()

    with pytest.raises(TypeError):
        service.import_sequences(
            ">gene1\nATGC",
            "dna",  # type: ignore[arg-type]
        )


def test_importer_accepts_injected_parser() -> None:
    parser = FastaParser()
    service = FastaImportService(parser=parser)

    sequences = service.import_sequences(
        ">gene1\nATGC",
        SequenceAlphabet.DNA,
    )

    assert sequences[0].name == "gene1"


def test_importer_rejects_invalid_parser() -> None:
    with pytest.raises(TypeError, match="FastaParser"):
        FastaImportService(parser=object())  # type: ignore[arg-type]
