
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationEvent:
    """
    Base contract for events exchanged inside Aditi.

    Event payloads are defined by individual event subclasses.
    """

    event_id: UUID = field(default_factory=uuid4)

    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    correlation_id: UUID | None = None
