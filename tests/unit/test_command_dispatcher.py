from dataclasses import dataclass

import pytest

from aditi.application.commands import (
    Command,
    CommandDispatcher,
    CommandDispatcherError,
    CommandHandler,
    CommandResponse,
)
from aditi.application.runtime.cancellation import CancellationToken


@dataclass(frozen=True, slots=True)
class LoadResourceCommand(Command):
    resource_id: str


@dataclass(frozen=True, slots=True)
class DeleteResourceCommand(Command):
    resource_id: str


class LoadResourceHandler(
    CommandHandler[LoadResourceCommand, dict[str, bool]]
):
    @property
    def command_type(self) -> type[LoadResourceCommand]:
        return LoadResourceCommand

    def handle(
        self,
        command: LoadResourceCommand,
        cancellation_token: CancellationToken,
    ) -> CommandResponse[dict[str, bool]]:
        return CommandResponse.ok(
            command_id=command.command_id,
            correlation_id=command.correlation_id,
            data={"loaded": True},
        )


class InvalidCommandHandler(
    CommandHandler[LoadResourceCommand, dict[str, bool]]
):
    @property
    def command_type(self) -> type[LoadResourceCommand]:
        return str

    def handle(
        self,
        command: LoadResourceCommand,
    ) -> CommandResponse[dict[str, bool]]:
        raise NotImplementedError


def test_register_handler():
    dispatcher = CommandDispatcher()

    dispatcher.register(LoadResourceHandler())

    assert dispatcher.handler_count == 1


def test_contains_registered_handler():
    dispatcher = CommandDispatcher()
    dispatcher.register(LoadResourceHandler())

    assert dispatcher.contains(LoadResourceCommand)
    assert not dispatcher.contains(DeleteResourceCommand)


def test_rejects_duplicate_handler_registration():
    dispatcher = CommandDispatcher()
    dispatcher.register(LoadResourceHandler())

    with pytest.raises(CommandDispatcherError):
        dispatcher.register(LoadResourceHandler())


def test_dispatches_command_to_registered_handler():
    dispatcher = CommandDispatcher()
    dispatcher.register(LoadResourceHandler())

    command = LoadResourceCommand(resource_id="pathway_001")
    response = dispatcher.dispatch(command)

    assert response.is_success
    assert response.data == {"loaded": True}
    assert response.command_id == command.command_id


def test_rejects_command_without_registered_handler():
    dispatcher = CommandDispatcher()
    command = DeleteResourceCommand(resource_id="pathway_001")

    with pytest.raises(CommandDispatcherError):
        dispatcher.dispatch(command)


def test_rejects_handler_with_invalid_command_type():
    dispatcher = CommandDispatcher()

    with pytest.raises(CommandDispatcherError):
        dispatcher.register(InvalidCommandHandler())