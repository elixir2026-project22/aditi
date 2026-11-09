
from uuid import UUID, uuid4

import pytest

from aditi.domain.entities.identity import EntityIdentity


def test_generate_entity_identity():
    identity = EntityIdentity.generate()

    assert isinstance(identity, EntityIdentity)
    assert isinstance(identity.value, UUID)


def test_entity_identity_generates_unique_values():
    first = EntityIdentity.generate()
    second = EntityIdentity.generate()

    assert first.value != second.value


def test_entity_identity_accepts_existing_uuid():
    identifier = uuid4()

    identity = EntityIdentity(value=identifier)

    assert identity.value == identifier


def test_entity_identity_is_immutable():
    identity = EntityIdentity.generate()

    with pytest.raises(AttributeError):
        identity.value = uuid4()


def test_entity_identity_equality():
    identifier = uuid4()

    first = EntityIdentity(value=identifier)
    second = EntityIdentity(value=identifier)

    assert first == second


def test_entity_identity_inequality():
    first = EntityIdentity.generate()
    second = EntityIdentity.generate()

    assert first != second


def test_entity_identity_is_hashable():
    first = EntityIdentity.generate()
    second = EntityIdentity.generate()

    identities = {first, second}

    assert len(identities) == 2


def test_entity_identity_string_representation():
    identifier = uuid4()
    identity = EntityIdentity(value=identifier)

    assert str(identity) == str(identifier)


@pytest.mark.parametrize(
    "invalid_value",
    [
        "not-a-uuid",
        123,
        None,
        {},
    ],
)
def test_entity_identity_rejects_invalid_values(invalid_value):
    with pytest.raises(TypeError, match="must be a UUID"):
        EntityIdentity(value=invalid_value)
