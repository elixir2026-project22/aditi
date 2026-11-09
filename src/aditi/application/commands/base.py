
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True, kw_only=True)
class Command:
    """
    Base contract for application commands.

    Individual commands define their own payload fields.
    """

    command_id: UUID = field(default_factory=uuid4)

    correlation_id: UUID | None = None

    issued_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
