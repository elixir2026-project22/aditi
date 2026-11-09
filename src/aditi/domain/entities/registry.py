
from __future__ import annotations

from aditi.domain.entities.base import BiologicalEntity
from aditi.domain.entities.identifiers import ExternalIdentifier
from aditi.domain.entities.identity import EntityIdentity


class EntityRegistryError(RuntimeError):
    """Raised when biological entity registration encounters an error."""


class EntityRegistry:
    """
    Maintains centralized lookup indexes for biological entities.

    Entities are indexed by their internal identity and their
    external biological database identifiers.
    """

    def __init__(self) -> None:
        self._entities: dict[EntityIdentity, BiologicalEntity] = {}

        self._external_index: dict[
            tuple[str, str],
            EntityIdentity,
        ] = {}

    @property
    def entities(self) -> tuple[BiologicalEntity, ...]:
        """Return registered entities in registration order."""
        return tuple(self._entities.values())

    def register(self, entity: BiologicalEntity) -> None:
        """Register a biological entity and its external identifiers."""

        if not isinstance(entity, BiologicalEntity):
            raise EntityRegistryError(
                "Registered objects must be BiologicalEntity instances."
            )

        identity = entity.identity

        if identity in self._entities:
            raise EntityRegistryError(
                f"Entity '{identity}' is already registered."
            )

        external_keys = [
            (identifier.namespace, identifier.value)
            for identifier in entity.external_identifiers
        ]

        for namespace, value in external_keys:
            existing_identity = self._external_index.get(
                (namespace, value)
            )

            if existing_identity is not None:
                raise EntityRegistryError(
                    f"External identifier '{namespace}:{value}' "
                    "is already assigned to another entity."
                )

        self._entities[identity] = entity

        for external_key in external_keys:
            self._external_index[external_key] = identity

    def get_by_identity(
        self,
        identity: EntityIdentity,
    ) -> BiologicalEntity | None:
        """Retrieve an entity using its internal identity."""

        if not isinstance(identity, EntityIdentity):
            raise TypeError(
                "Entity lookup requires an EntityIdentity."
            )

        return self._entities.get(identity)

    def get_by_external_identifier(
        self,
        identifier: ExternalIdentifier,
    ) -> BiologicalEntity | None:
        """Retrieve an entity using an external database identifier."""

        if not isinstance(identifier, ExternalIdentifier):
            raise TypeError(
                "External identifier lookup requires an ExternalIdentifier."
            )

        external_key = (
            identifier.namespace,
            identifier.value,
        )

        identity = self._external_index.get(external_key)

        if identity is None:
            return None

        return self._entities.get(identity)

    def contains(self, identity: EntityIdentity) -> bool:
        """Check whether an internal entity identity is registered."""

        if not isinstance(identity, EntityIdentity):
            raise TypeError(
                "Entity lookup requires an EntityIdentity."
            )

        return identity in self._entities
