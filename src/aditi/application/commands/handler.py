from abc import ABC, abstractmethod

from aditi.application.commands.base import Command
from aditi.application.commands.response import CommandResponse
from aditi.application.runtime.cancellation import CancellationToken


class CommandHandler[CommandT: Command, ResultT](ABC):
    """
    Base contract for all application command handlers.

    Handlers receive a cancellation token so long-running
    operations can respond to cancellation requests.
    """

    @property
    @abstractmethod
    def command_type(self) -> type[CommandT]:
        """Return the command type handled by this handler."""
        raise NotImplementedError

    @abstractmethod
    def handle(
        self,
        command: CommandT,
        cancellation_token: CancellationToken,
    ) -> CommandResponse[ResultT]:
        """Execute a command and return its response."""
        raise NotImplementedError