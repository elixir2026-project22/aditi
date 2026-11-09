
from abc import ABC, abstractmethod

from aditi.application.runtime.context import ApplicationContext


class ApplicationModule(ABC):
    """
    Base contract for all Aditi application modules.

    Modules own their internal implementation and communicate
    through explicitly defined runtime interfaces.
    """

    @property
    @abstractmethod
    def module_id(self) -> str:
        """Return the unique identifier of this module."""
        raise NotImplementedError

    @property
    def dependencies(self) -> tuple[str, ...]:
        """
        Return the identifiers of modules this module depends on.

        Override this property when dependencies are required.
        """
        return ()

    def initialize(self, context: ApplicationContext) -> None:
        """Prepare the module and acquire required resources."""

    def start(self) -> None:
        """Start module operations."""

    def update(self, delta_seconds: float) -> None:
        """Process one runtime update."""

    def stop(self) -> None:
        """Stop ongoing module operations."""

    def shutdown(self) -> None:
        """Release module-owned resources."""
