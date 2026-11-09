
from dataclasses import dataclass
from uuid import uuid4

import pytest

from aditi.application.commands import (
    Command,
    CommandResponse,
    ErrorInfo,
)


@dataclass(frozen=True, slots=True)
class ExampleCommand(Command):
    resource_id: str


def test_command_generates_unique_identifier():
    first = ExampleCommand(resource_id="pathway_001")
    second = ExampleCommand(resource_id="pathway_002")

    assert first.command_id != second.command_id


def test_command_has_utc_timestamp():
    command = ExampleCommand(resource_id="pathway_001")

    assert command.issued_at.tzinfo is not None
    assert command.issued_at.utcoffset().total_seconds() == 0


def test_command_accepts_correlation_identifier():
    correlation_id = uuid4()

    command = ExampleCommand(
        resource_id="pathway_001",
        correlation_id=correlation_id,
    )

    assert command.correlation_id == correlation_id


def test_command_is_immutable():
    command = ExampleCommand(resource_id="pathway_001")

    with pytest.raises(AttributeError):
        command.resource_id = "pathway_002"


def test_successful_response():
    command_id = uuid4()
    correlation_id = uuid4()

    response = CommandResponse.ok(
        command_id=command_id,
        correlation_id=correlation_id,
        data={"loaded": True},
    )

    assert response.is_success is True
    assert response.command_id == command_id
    assert response.correlation_id == correlation_id
    assert response.data == {"loaded": True}
    assert response.error is None


def test_successful_response_without_data():
    response = CommandResponse.ok(
        command_id=uuid4(),
        correlation_id=None,
    )

    assert response.is_success is True
    assert response.data is None


def test_failed_response():
    command_id = uuid4()

    error = ErrorInfo(
        code="RESOURCE_NOT_FOUND",
        message="Requested pathway does not exist.",
    )

    response = CommandResponse.failure(
        command_id=command_id,
        correlation_id=None,
        error=error,
    )

    assert response.is_success is False
    assert response.command_id == command_id
    assert response.error is error
    assert response.data is None


def test_error_info_supports_details():
    error = ErrorInfo(
        code="INVALID_SEQUENCE",
        message="Sequence format is invalid.",
        details={"line": 12, "format": "FASTA"},
    )

    assert error.code == "INVALID_SEQUENCE"
    assert error.details["line"] == 12


def test_successful_response_rejects_error():
    with pytest.raises(ValueError):
        CommandResponse(
            command_id=uuid4(),
            correlation_id=None,
            is_success=True,
            error=ErrorInfo(
                code="ERROR",
                message="Unexpected error.",
            ),
        )


def test_failed_response_requires_error():
    with pytest.raises(ValueError):
        CommandResponse(
            command_id=uuid4(),
            correlation_id=None,
            is_success=False,
        )


def test_response_has_utc_completion_timestamp():
    response = CommandResponse.ok(
        command_id=uuid4(),
        correlation_id=None,
    )

    assert response.completed_at.tzinfo is not None
    assert response.completed_at.utcoffset().total_seconds() == 0


