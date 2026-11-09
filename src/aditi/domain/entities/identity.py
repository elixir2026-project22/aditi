
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class EntityIdentity:
    """
    Represents the unique internal identity of a biological entity.

    Entity identities are generated independently of external
    biological database identifiers.
    """

    value: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise TypeError(
                "Entity identity value must be a UUID."
            )

    @classmethod
    def generate(cls) -> EntityIdentity:
        """Generate a new unique entity identity."""
        return cls()

    def __str__(self) -> str:
        """Return the UUID as a string."""
        return str(self.value)
