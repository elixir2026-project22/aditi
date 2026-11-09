from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ErrorInfo:
    """Structured information describing a command failure."""

    code: str
    message: str
    details: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CommandResponse[T]:
    """
    Represents the result of executing an application command.

    Successful responses carry result data.
    Failed responses carry structured error information.
    """

    command_id: UUID
    correlation_id: UUID | None
    is_success: bool

    data: T | None = None
    error: ErrorInfo | None = None

    completed_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    def __post_init__(self) -> None:
        if self.is_success and self.error is not None:
            raise ValueError(
                "Successful responses cannot contain an error."
            )

        if not self.is_success and self.error is None:
            raise ValueError(
                "Failed responses must contain error information."
            )

    @classmethod
    def ok(
        cls,
        command_id: UUID,
        correlation_id: UUID | None,
        data: T | None = None,
    ) -> CommandResponse[T]:
        """Create a successful command response."""

        return cls(
            command_id=command_id,
            correlation_id=correlation_id,
            is_success=True,
            data=data,
        )

    @classmethod
    def failure(
        cls,
        command_id: UUID,
        correlation_id: UUID | None,
        error: ErrorInfo,
    ) -> CommandResponse[T]:
        """Create a failed command response."""

        return cls(
            command_id=command_id,
            correlation_id=correlation_id,
            is_success=False,
            error=error,
        )