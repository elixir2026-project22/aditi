from collections.abc import Mapping


class ApplicationError(Exception):
    """
    Base exception for expected Aditi application failures.

    Provides a stable error code and optional structured details
    independently of the exception's display message.
    """

    code = "APPLICATION_ERROR"

    def __init__(
        self,
        message: str,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = dict(details or {})


class ValidationError(ApplicationError):
    """Raised when application input or data fails validation."""

    code = "VALIDATION_ERROR"


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource cannot be found."""

    code = "RESOURCE_NOT_FOUND"


class ResourceConflictError(ApplicationError):
    """Raised when an operation conflicts with existing resource state."""

    code = "RESOURCE_CONFLICT"