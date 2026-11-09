
from dataclasses import FrozenInstanceError

import pytest

from aditi.domain.entities.base import BiologicalEntity
from aditi.domain.entities.identifiers import ExternalIdentifier
from aditi.domain.entities.identity import EntityIdentity


class ExampleEntity(BiologicalEntity):

    @property
    def entity_type(self) -> str:
        return "example"


def test_create_biological_entity():
    entity = ExampleEntity()

    assert isinstance(entity.identity, EntityIdentity)
    assert entity.external_identifiers == ()
    assert entity.entity_type == "example"


def test_biological_entity_generates_unique_identity():
    first = ExampleEntity()
    second = ExampleEntity()

    assert first.identity != second.identity


def test_biological_entity_accepts_existing_identity():
    identity = EntityIdentity.generate()

    entity = ExampleEntity(identity=identity)

    assert entity.identity == identity


def test_biological_entity_accepts_external_identifiers():
    identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    entity = ExampleEntity(
        external_identifiers=(identifier,),
    )

    assert entity.external_identifiers == (identifier,)


def test_biological_entity_accepts_multiple_external_identifiers():
    identifiers = (
        ExternalIdentifier(
            namespace="UniProt",
            value="P04637",
        ),
        ExternalIdentifier(
            namespace="PDB",
            value="1TUP",
        ),
    )

    entity = ExampleEntity(
        external_identifiers=identifiers,
    )

    assert entity.external_identifiers == identifiers


def test_biological_entity_is_abstract():
    with pytest.raises(TypeError):
        BiologicalEntity()


def test_biological_entity_rejects_invalid_identity():
    with pytest.raises(TypeError, match="EntityIdentity"):
        ExampleEntity(identity="invalid")


@pytest.mark.parametrize(
    "identifiers",
    [
        ["UniProt:P04637"],
        "UniProt:P04637",
        None,
    ],
)
def test_biological_entity_rejects_non_tuple_identifiers(identifiers):
    with pytest.raises(TypeError, match="tuple"):
        ExampleEntity(external_identifiers=identifiers)


def test_biological_entity_rejects_invalid_identifier_objects():
    with pytest.raises(TypeError, match="ExternalIdentifier"):
        ExampleEntity(
            external_identifiers=("UniProt:P04637",),
        )


def test_biological_entity_rejects_duplicate_external_identifiers():
    identifiers = (
        ExternalIdentifier(
            namespace="UniProt",
            value="P04637",
        ),
        ExternalIdentifier(
            namespace="UniProt",
            value="P04637",
            url="https://www.uniprot.org/uniprotkb/P04637",
        ),
    )

    with pytest.raises(ValueError, match="duplicate"):
        ExampleEntity(external_identifiers=identifiers)


def test_biological_entity_is_immutable():
    entity = ExampleEntity()

    with pytest.raises(FrozenInstanceError):
        entity.identity = EntityIdentity.generate()


def test_biological_entity_external_identifiers_are_immutable():
    entity = ExampleEntity()

    with pytest.raises(FrozenInstanceError):
        entity.external_identifiers = ()


def test_biological_entity_equality():
    identity = EntityIdentity.generate()

    first = ExampleEntity(identity=identity)
    second = ExampleEntity(identity=identity)

    assert first == second
