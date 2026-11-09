
from dataclasses import dataclass

import pytest

from aditi.application.commands import (
    Command,
    CommandDispatcher,
    CommandHandler,
    CommandResponse,
)
from aditi.application.runtime.cancellation import (
    CancellationToken,
    CancellationTokenSource,
    OperationCancelledError,
)


@dataclass(frozen=True, slots=True)
class ProcessCommand(Command):
    operation: str


class ProcessHandler(CommandHandler[ProcessCommand, str]):
    def __init__(self) -> None:
        self.received_token: CancellationToken | None = None

    @property
    def command_type(self) -> type[ProcessCommand]:
        return ProcessCommand

    def handle(
        self,
        command: ProcessCommand,
        cancellation_token: CancellationToken,
    ) -> CommandResponse[str]:
        self.received_token = cancellation_token

        cancellation_token.throw_if_cancelled()

        return CommandResponse.ok(
            command_id=command.command_id,
            correlation_id=command.correlation_id,
            data=f"Completed: {command.operation}",
        )


def test_dispatcher_forwards_cancellation_token():
    dispatcher = CommandDispatcher()
    handler = ProcessHandler()
    source = CancellationTokenSource()

    dispatcher.register(handler)

    dispatcher.dispatch(
        ProcessCommand(operation="alignment"),
        source.token,
    )

    assert handler.received_token is source.token


def test_dispatcher_creates_default_cancellation_token():
    dispatcher = CommandDispatcher()
    handler = ProcessHandler()

    dispatcher.register(handler)

    response = dispatcher.dispatch(
        ProcessCommand(operation="alignment")
    )

    assert response.is_success
    assert handler.received_token is not None
    assert not handler.received_token.is_cancelled


def test_dispatcher_rejects_already_cancelled_operation():
    dispatcher = CommandDispatcher()
    handler = ProcessHandler()
    source = CancellationTokenSource()

    dispatcher.register(handler)
    source.cancel()

    with pytest.raises(OperationCancelledError):
        dispatcher.dispatch(
            ProcessCommand(operation="alignment"),
            source.token,
        )

    assert handler.received_token is None


def test_handler_can_observe_cancellation_during_execution():
    source = CancellationTokenSource()

    class CancellingHandler(ProcessHandler):
        def handle(
            self,
            command: ProcessCommand,
            cancellation_token: CancellationToken,
        ) -> CommandResponse[str]:
            source.cancel()

            return super().handle(command, cancellation_token)

    dispatcher = CommandDispatcher()
    handler = CancellingHandler()

    dispatcher.register(handler)

    with pytest.raises(OperationCancelledError):
        dispatcher.dispatch(
            ProcessCommand(operation="alignment"),
            source.token,
        )

    assert handler.received_token is source.token
