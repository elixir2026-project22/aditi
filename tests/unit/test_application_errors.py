import pytest

from aditi.application.errors import (
    ApplicationError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)


@pytest.mark.parametrize(
    ("error_type", "expected_code"),
    [
        (ApplicationError, "APPLICATION_ERROR"),
        (ValidationError, "VALIDATION_ERROR"),
        (ResourceNotFoundError, "RESOURCE_NOT_FOUND"),
        (ResourceConflictError, "RESOURCE_CONFLICT"),
    ],
)
def test_application_error_codes(error_type, expected_code):
    error = error_type("Something went wrong.")

    assert error.code == expected_code


def test_application_error_preserves_message():
    error = ApplicationError("Unable to complete operation.")

    assert str(error) == "Unable to complete operation."
    assert error.message == "Unable to complete operation."


def test_application_error_supports_details():
    error = ValidationError(
        "Invalid sequence.",
        details={
            "line": 12,
            "format": "FASTA",
        },
    )

    assert error.details["line"] == 12
    assert error.details["format"] == "FASTA"


def test_application_error_uses_empty_details_by_default():
    error = ApplicationError("Unexpected application failure.")

    assert error.details == {}


def test_application_error_is_a_standard_exception():
    with pytest.raises(ApplicationError):
        raise ResourceNotFoundError("Pathway not found.")