
import pytest

from aditi.domain.entities.base import BiologicalEntity
from aditi.domain.entities.identifiers import ExternalIdentifier
from aditi.domain.entities.identity import EntityIdentity
from aditi.domain.entities.registry import (
    EntityRegistry,
    EntityRegistryError,
)


class ExampleEntity(BiologicalEntity):

    @property
    def entity_type(self) -> str:
        return "example"


def test_register_entity():
    registry = EntityRegistry()
    entity = ExampleEntity()

    registry.register(entity)

    assert registry.get_by_identity(entity.identity) is entity


def test_retrieve_entity_by_internal_identity():
    registry = EntityRegistry()
    entity = ExampleEntity()

    registry.register(entity)

    result = registry.get_by_identity(entity.identity)

    assert result is entity


def test_return_none_for_unknown_internal_identity():
    registry = EntityRegistry()

    result = registry.get_by_identity(
        EntityIdentity.generate()
    )

    assert result is None


def test_register_entity_with_external_identifier():
    registry = EntityRegistry()

    identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    entity = ExampleEntity(
        external_identifiers=(identifier,),
    )

    registry.register(entity)

    assert registry.get_by_external_identifier(identifier) is entity


def test_retrieve_entity_using_external_identifier():
    registry = EntityRegistry()

    registered_identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    lookup_identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
        url="https://www.uniprot.org/uniprotkb/P04637",
    )

    entity = ExampleEntity(
        external_identifiers=(registered_identifier,),
    )

    registry.register(entity)

    assert registry.get_by_external_identifier(lookup_identifier) is entity


def test_return_none_for_unknown_external_identifier():
    registry = EntityRegistry()

    identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    assert registry.get_by_external_identifier(identifier) is None


def test_register_multiple_entities():
    registry = EntityRegistry()

    first = ExampleEntity()
    second = ExampleEntity()

    registry.register(first)
    registry.register(second)

    assert registry.get_by_identity(first.identity) is first
    assert registry.get_by_identity(second.identity) is second
    assert len(registry.entities) == 2


def test_prevent_duplicate_internal_identity():
    registry = EntityRegistry()

    identity = EntityIdentity.generate()

    first = ExampleEntity(identity=identity)
    second = ExampleEntity(identity=identity)

    registry.register(first)

    with pytest.raises(EntityRegistryError, match="already registered"):
        registry.register(second)


def test_prevent_duplicate_external_identifier():
    registry = EntityRegistry()

    identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    first = ExampleEntity(
        external_identifiers=(identifier,),
    )

    second = ExampleEntity(
        external_identifiers=(identifier,),
    )

    registry.register(first)

    with pytest.raises(EntityRegistryError, match="already assigned"):
        registry.register(second)


def test_allow_same_value_in_different_namespaces():
    registry = EntityRegistry()

    first_identifier = ExternalIdentifier(
        namespace="UniProt",
        value="12345",
    )

    second_identifier = ExternalIdentifier(
        namespace="PDB",
        value="12345",
    )

    first = ExampleEntity(
        external_identifiers=(first_identifier,),
    )

    second = ExampleEntity(
        external_identifiers=(second_identifier,),
    )

    registry.register(first)
    registry.register(second)

    assert registry.get_by_external_identifier(first_identifier) is first
    assert registry.get_by_external_identifier(second_identifier) is second


def test_registration_is_atomic_when_external_identifier_conflicts():
    registry = EntityRegistry()

    existing_identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    first = ExampleEntity(
        external_identifiers=(existing_identifier,),
    )

    registry.register(first)

    unique_identifier = ExternalIdentifier(
        namespace="PDB",
        value="1TUP",
    )

    conflicting_identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    second = ExampleEntity(
        external_identifiers=(
            unique_identifier,
            conflicting_identifier,
        ),
    )

    with pytest.raises(EntityRegistryError):
        registry.register(second)

    assert registry.get_by_external_identifier(unique_identifier) is None
    assert registry.get_by_identity(second.identity) is None
    assert len(registry.entities) == 1


def test_contains_registered_entity():
    registry = EntityRegistry()
    entity = ExampleEntity()

    registry.register(entity)

    assert registry.contains(entity.identity)


def test_contains_returns_false_for_unknown_entity():
    registry = EntityRegistry()

    assert not registry.contains(EntityIdentity.generate())


def test_reject_non_biological_entity():
    registry = EntityRegistry()

    with pytest.raises(EntityRegistryError, match="BiologicalEntity"):
        registry.register(object())


def test_reject_invalid_internal_identity_lookup():
    registry = EntityRegistry()

    with pytest.raises(TypeError, match="EntityIdentity"):
        registry.get_by_identity("invalid")


def test_reject_invalid_external_identifier_lookup():
    registry = EntityRegistry()

    with pytest.raises(TypeError, match="ExternalIdentifier"):
        registry.get_by_external_identifier("UniProt:P04637")


def test_entities_returns_tuple():
    registry = EntityRegistry()
    entity = ExampleEntity()

    registry.register(entity)

    assert isinstance(registry.entities, tuple)
    assert registry.entities == (entity,)


def test_entities_preserve_registration_order():
    registry = EntityRegistry()

    first = ExampleEntity()
    second = ExampleEntity()
    third = ExampleEntity()

    registry.register(first)
    registry.register(second)
    registry.register(third)

    assert registry.entities == (first, second, third)
