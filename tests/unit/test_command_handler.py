
from dataclasses import dataclass

import pytest

from aditi.application.commands import (
    Command,
    CommandHandler,
    CommandResponse,
)
from aditi.application.runtime.cancellation import (
    CancellationToken,
    CancellationTokenSource,
)


@dataclass(frozen=True, slots=True)
class LoadResourceCommand(Command):
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
        cancellation_token.throw_if_cancelled()

        return CommandResponse.ok(
            command_id=command.command_id,
            correlation_id=command.correlation_id,
            data={"loaded": True},
        )


def test_handler_declares_command_type():
    handler = LoadResourceHandler()

    assert handler.command_type is LoadResourceCommand


def test_handler_executes_command():
    handler = LoadResourceHandler()
    command = LoadResourceCommand(resource_id="pathway_001")
    token = CancellationTokenSource().token

    response = handler.handle(command, token)

    assert response.is_success
    assert response.data == {"loaded": True}


def test_handler_preserves_command_identifier():
    handler = LoadResourceHandler()
    command = LoadResourceCommand(resource_id="pathway_001")
    token = CancellationTokenSource().token

    response = handler.handle(command, token)

    assert response.command_id == command.command_id


def test_handler_preserves_correlation_identifier():
    correlation_id = CancellationTokenSource().token

    command = LoadResourceCommand(
        resource_id="pathway_001",
        correlation_id=None,
    )

    response = LoadResourceHandler().handle(command, correlation_id)

    assert response.correlation_id == command.correlation_id


def test_handler_contract_is_abstract():
    with pytest.raises(TypeError):
        CommandHandler()


