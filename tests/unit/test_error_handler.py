import pytest

from aditi.application.errors import (
    ApplicationError,
    ResourceNotFoundError,
    ValidationError,
)
from aditi.application.runtime import (
    ErrorHandler,
    OperationCancelledError,
)


def test_handles_application_error():
    handler = ErrorHandler()
    error = ApplicationError("Application failure.")

    result = handler.handle(error)

    assert result.code == "APPLICATION_ERROR"
    assert result.message == "Application failure."


def test_preserves_validation_error_details():
    handler = ErrorHandler()

    error = ValidationError(
        "Invalid sequence.",
        details={"line": 12, "format": "FASTA"},
    )

    result = handler.handle(error)

    assert result.code == "VALIDATION_ERROR"
    assert result.details["line"] == 12
    assert result.details["format"] == "FASTA"


def test_handles_resource_not_found_error():
    handler = ErrorHandler()
    error = ResourceNotFoundError("Pathway not found.")

    result = handler.handle(error)

    assert result.code == "RESOURCE_NOT_FOUND"
    assert result.message == "Pathway not found."


def test_handles_unexpected_exception():
    handler = ErrorHandler()
    error = RuntimeError("Unexpected failure.")

    result = handler.handle(error)

    assert result.code == "INTERNAL_ERROR"
    assert result.message == "An unexpected internal error occurred."


def test_does_not_expose_unexpected_exception_message():
    handler = ErrorHandler()
    error = RuntimeError("Database password was invalid.")

    result = handler.handle(error)

    assert "Database password" not in result.message
    assert result.details == {}


def test_propagates_operation_cancellation():
    handler = ErrorHandler()
    error = OperationCancelledError("Operation stopped.")

    with pytest.raises(OperationCancelledError):
        handler.handle(error)


def test_handles_different_unexpected_exception_types():
    handler = ErrorHandler()

    errors = [
        ValueError("Invalid value."),
        TypeError("Invalid type."),
        OSError("System failure."),
    ]

    for error in errors:
        result = handler.handle(error)

        assert result.code == "INTERNAL_ERROR"