
from __future__ import annotations

from typing import TYPE_CHECKING

from aditi.application.errors import ApplicationError
from aditi.application.runtime.cancellation import OperationCancelledError

if TYPE_CHECKING:
    from aditi.application.commands.response import ErrorInfo


class ErrorHandler:
    """
    Converts application exceptions into structured error information.

    Expected application errors retain their defined details.
    Unexpected exceptions are represented by a generic error.
    Cancellation is propagated rather than treated as a failure.
    """

    INTERNAL_ERROR_CODE = "INTERNAL_ERROR"
    INTERNAL_ERROR_MESSAGE = "An unexpected internal error occurred."

    def handle(self, error: Exception) -> ErrorInfo:
        """Convert an exception into structured error information."""

        if isinstance(error, OperationCancelledError):
            raise error

        from aditi.application.commands.response import ErrorInfo

        if isinstance(error, ApplicationError):
            return ErrorInfo(
                code=error.code,
                message=error.message,
                details=error.details,
            )

        return ErrorInfo(
            code=self.INTERNAL_ERROR_CODE,
            message=self.INTERNAL_ERROR_MESSAGE,
        )
