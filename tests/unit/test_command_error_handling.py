from dataclasses import dataclass

import pytest

from aditi.application.commands import (
    Command,
    CommandDispatcher,
    CommandDispatcherError,
    CommandHandler,
    CommandResponse,
)
from aditi.application.errors import ValidationError
from aditi.application.runtime.cancellation import (
    CancellationToken,
    OperationCancelledError,
)


@dataclass(frozen=True, slots=True)
class ValidateCommand(Command):
    sequence: str


class SuccessfulHandler(CommandHandler[ValidateCommand, str]):
    @property
    def command_type(self) -> type[ValidateCommand]:
        return ValidateCommand

    def handle(
        self,
        command: ValidateCommand,
        cancellation_token: CancellationToken,
    ) -> CommandResponse[str]:
        return CommandResponse.ok(
            command_id=command.command_id,
            correlation_id=command.correlation_id,
            data="Sequence validated.",
        )


class ValidationFailureHandler(SuccessfulHandler):
    def handle(
        self,
        command: ValidateCommand,
        cancellation_token: CancellationToken,
    ) -> CommandResponse[str]:
        raise ValidationError(
            "Invalid biological sequence.",
            details={"field": "sequence"},
        )


class UnexpectedFailureHandler(SuccessfulHandler):
    def handle(
        self,
        command: ValidateCommand,
        cancellation_token: CancellationToken,
    ) -> CommandResponse[str]:
        raise RuntimeError("Internal database failure.")


class CancellationHandler(SuccessfulHandler):
    def handle(
        self,
        command: ValidateCommand,
        cancellation_token: CancellationToken,
    ) -> CommandResponse[str]:
        raise OperationCancelledError("Operation stopped.")


def test_successful_command_returns_success_response():
    dispatcher = CommandDispatcher()
    dispatcher.register(SuccessfulHandler())

    command = ValidateCommand(sequence="ATGC")
    response = dispatcher.dispatch(command)

    assert response.is_success
    assert response.data == "Sequence validated."
    assert response.command_id == command.command_id


def test_application_error_becomes_failure_response():
    dispatcher = CommandDispatcher()
    dispatcher.register(ValidationFailureHandler())

    command = ValidateCommand(sequence="INVALID")
    response = dispatcher.dispatch(command)

    assert not response.is_success
    assert response.error is not None
    assert response.error.code == "VALIDATION_ERROR"
    assert response.error.message == "Invalid biological sequence."
    assert response.error.details["field"] == "sequence"


def test_unexpected_error_becomes_generic_failure_response():
    dispatcher = CommandDispatcher()
    dispatcher.register(UnexpectedFailureHandler())

    command = ValidateCommand(sequence="ATGC")
    response = dispatcher.dispatch(command)

    assert not response.is_success
    assert response.error is not None
    assert response.error.code == "INTERNAL_ERROR"
    assert response.error.message == (
        "An unexpected internal error occurred."
    )
    assert "Internal database failure" not in response.error.message


def test_failure_response_preserves_command_identifiers():
    dispatcher = CommandDispatcher()
    dispatcher.register(ValidationFailureHandler())

    command = ValidateCommand(sequence="INVALID")
    response = dispatcher.dispatch(command)

    assert response.command_id == command.command_id
    assert response.correlation_id == command.correlation_id


def test_cancellation_still_propagates():
    dispatcher = CommandDispatcher()
    dispatcher.register(CancellationHandler())

    command = ValidateCommand(sequence="ATGC")

    with pytest.raises(OperationCancelledError):
        dispatcher.dispatch(command)


def test_missing_handler_error_is_not_converted():
    dispatcher = CommandDispatcher()
    command = ValidateCommand(sequence="ATGC")

    with pytest.raises(CommandDispatcherError):
        dispatcher.dispatch(command)