from typing import cast

from aditi.application.commands.base import Command
from aditi.application.commands.handler import CommandHandler
from aditi.application.commands.response import CommandResponse
from aditi.application.runtime.cancellation import (
    CancellationToken,
    CancellationTokenSource,
    OperationCancelledError,
)
from aditi.application.runtime.error_handler import ErrorHandler


class CommandDispatcherError(RuntimeError):
    """Raised when command registration or dispatching fails."""


class CommandDispatcher:
    """
    Routes application commands to their registered handlers.

    Each command type can have exactly one registered handler.
    Handler execution errors are converted into structured responses.
    """

    def __init__(
        self,
        error_handler: ErrorHandler | None = None,
    ) -> None:
        self._handlers: dict[type[Command], CommandHandler] = {}
        self._error_handler = error_handler or ErrorHandler()

    @property
    def handler_count(self) -> int:
        """Return the number of registered command handlers."""
        return len(self._handlers)

    def register(self, handler: CommandHandler) -> None:
        """Register a handler for its declared command type."""

        command_type = handler.command_type

        if not isinstance(command_type, type) or not issubclass(
            command_type, Command
        ):
            raise CommandDispatcherError(
                "Handler must declare a valid Command subclass."
            )

        if command_type in self._handlers:
            raise CommandDispatcherError(
                f"A handler for '{command_type.__name__}' "
                "is already registered."
            )

        self._handlers[command_type] = handler

    def dispatch(
        self,
        command: Command,
        cancellation_token: CancellationToken | None = None,
    ) -> CommandResponse[object]:
        """
        Execute a command through its registered handler.

        Handler exceptions are converted into failure responses.
        Cancellation exceptions are allowed to propagate.
        """

        command_type = type(command)
        handler = self._handlers.get(command_type)

        if handler is None:
            raise CommandDispatcherError(
                f"No handler registered for '{command_type.__name__}'."
            )

        if cancellation_token is None:
            cancellation_token = CancellationTokenSource().token

        cancellation_token.throw_if_cancelled()

        try:
            return cast(
                CommandResponse[object],
                handler.handle(command, cancellation_token),
            )

        except OperationCancelledError:
            raise

        except Exception as error: #noqa BLE001
            error_info = self._error_handler.handle(error)

            return CommandResponse.failure(
                command_id=command.command_id,
                correlation_id=command.correlation_id,
                error=error_info,
            )

    def contains(self, command_type: type[Command]) -> bool:
        """Check whether a handler is registered for a command type."""
        return command_type in self._handlers