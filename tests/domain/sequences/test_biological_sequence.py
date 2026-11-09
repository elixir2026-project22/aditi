
from dataclasses import FrozenInstanceError

import pytest

from aditi.domain.sequences.alphabet import SequenceAlphabet
from aditi.domain.sequences.biological_sequence import BiologicalSequence


@pytest.mark.parametrize(
    ("alphabet", "residues"),
    [
        (SequenceAlphabet.DNA, "ATGCGT"),
        (SequenceAlphabet.RNA, "AUGCGU"),
        (SequenceAlphabet.PROTEIN, "MKWVTF"),
    ],
)
def test_biological_sequence_accepts_valid_residues(
    alphabet: SequenceAlphabet,
    residues: str,
) -> None:
    sequence = BiologicalSequence(
        name="Example Sequence",
        residues=residues,
        alphabet=alphabet,
    )

    assert sequence.name == "Example Sequence"
    assert sequence.residues == residues
    assert sequence.alphabet is alphabet
    assert sequence.length == len(residues)
    assert sequence.entity_type == "sequence"


@pytest.mark.parametrize(
    ("alphabet", "residues"),
    [
        (SequenceAlphabet.DNA, "ATUG"),
        (SequenceAlphabet.RNA, "ATCG"),
        (SequenceAlphabet.PROTEIN, "MKW*"),
    ],
)
def test_biological_sequence_rejects_invalid_residues(
    alphabet: SequenceAlphabet,
    residues: str,
) -> None:
    with pytest.raises(ValueError):
        BiologicalSequence(
            name="Invalid Sequence",
            residues=residues,
            alphabet=alphabet,
        )


def test_biological_sequence_rejects_empty_residues() -> None:
    with pytest.raises(ValueError):
        BiologicalSequence(
            name="Empty Sequence",
            residues="",
            alphabet=SequenceAlphabet.DNA,
        )


@pytest.mark.parametrize("name", ["", " ", "  Sequence", "Sequence  "])
def test_biological_sequence_rejects_invalid_names(
    name: str,
) -> None:
    with pytest.raises(ValueError):
        BiologicalSequence(
            name=name,
            residues="ATGC",
            alphabet=SequenceAlphabet.DNA,
        )


def test_biological_sequence_rejects_invalid_alphabet_type() -> None:
    with pytest.raises(TypeError):
        BiologicalSequence(
            name="Example",
            residues="ATGC",
            alphabet="dna",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("description", ["", " ", "  Example", "Example  "])
def test_biological_sequence_rejects_invalid_descriptions(
    description: str,
) -> None:
    with pytest.raises(ValueError):
        BiologicalSequence(
            name="Example",
            residues="ATGC",
            alphabet=SequenceAlphabet.DNA,
            description=description,
        )


def test_biological_sequence_accepts_description() -> None:
    sequence = BiologicalSequence(
        name="Example",
        residues="ATGC",
        alphabet=SequenceAlphabet.DNA,
        description="Example DNA sequence.",
    )

    assert sequence.description == "Example DNA sequence."


def test_biological_sequence_is_immutable() -> None:
    sequence = BiologicalSequence(
        name="Example",
        residues="ATGC",
        alphabet=SequenceAlphabet.DNA,
    )

    with pytest.raises(FrozenInstanceError):
        sequence.name = "Modified"  # type: ignore[misc]
