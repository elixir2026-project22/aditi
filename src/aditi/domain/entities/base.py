
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from aditi.domain.entities.identifiers import ExternalIdentifier
from aditi.domain.entities.identity import EntityIdentity


@dataclass(frozen=True, slots=True)
class BiologicalEntity(ABC):
    """
    Base contract for all biological entities in Aditi.

    Every biological entity has an internal identity and may
    reference multiple external biological database identifiers.
    """

    identity: EntityIdentity = field(
        default_factory=EntityIdentity.generate
    )

    external_identifiers: tuple[ExternalIdentifier, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not isinstance(self.identity, EntityIdentity):
            raise TypeError(
                "Biological entity identity must be an EntityIdentity."
            )

        if not isinstance(self.external_identifiers, tuple):
            raise TypeError(
                "External identifiers must be provided as a tuple."
            )

        seen_identifiers: set[tuple[str, str]] = set()

        for identifier in self.external_identifiers:
            if not isinstance(identifier, ExternalIdentifier):
                raise TypeError(
                    "All external identifiers must be ExternalIdentifier instances."
                )

            identifier_key = (
                identifier.namespace,
                identifier.value,
            )

            if identifier_key in seen_identifiers:
                raise ValueError(
                    "Biological entity cannot contain duplicate "
                    "external identifiers."
                )

            seen_identifiers.add(identifier_key)

    @property
    @abstractmethod
    def entity_type(self) -> str:
        """Return the biological entity type."""
        raise NotImplementedError
