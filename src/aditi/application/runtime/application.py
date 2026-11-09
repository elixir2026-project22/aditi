
from math import isfinite
from threading import Event
from time import perf_counter

from aditi.application.modules.manager import ModuleManager
from aditi.application.runtime.context import ApplicationContext
from aditi.application.runtime.module_runtime import (
    ModuleRuntime,
    ModuleRuntimeError,
    RuntimeState,
)
from aditi.infrastructure.logging import (
    LoggingConfig,
    configure_logging,
    get_logger,
)


class Application:
    """
    Main application coordinator for Aditi.

    Owns application context, logging configuration,
    module runtime lifecycle, and the continuous update loop.
    """

    def __init__(
        self,
        module_manager: ModuleManager,
        context: ApplicationContext | None = None,
        logging_config: LoggingConfig | None = None,
        target_update_rate_hz: float = 60.0,
    ) -> None:
        if (
            not isfinite(target_update_rate_hz)
            or target_update_rate_hz <= 0
        ):
            raise ValueError(
                "Target update rate must be a finite, positive value."
            )

        self._context = context or ApplicationContext()
        self._logging_config = logging_config or LoggingConfig()
        self._target_update_rate_hz = target_update_rate_hz
        self._stop_event = Event()

        self._runtime = ModuleRuntime(
            manager=module_manager,
            context=self._context,
        )

        self._logger = get_logger("application")

    @property
    def state(self) -> RuntimeState:
        """Return the current application runtime state."""

        return self._runtime.state

    @property
    def context(self) -> ApplicationContext:
        """Return the shared application context."""

        return self._context

    @property
    def target_update_rate_hz(self) -> float:
        """Return the configured target update rate."""

        return self._target_update_rate_hz

    def initialize(self) -> None:
        """Configure logging and initialize application modules."""

        configure_logging(self._logging_config)

        self._logger.info(
            "Initializing application: %s",
            self._context.application_name,
        )

        self._runtime.initialize()

        self._logger.info(
            "Application initialized: %s",
            self._context.application_name,
        )

    def start(self) -> None:
        """Start the application runtime."""

        self._stop_event.clear()

        self._logger.info("Starting application.")

        self._runtime.start()

        self._logger.info("Application started.")

    def update(self, delta_seconds: float) -> None:
        """Forward an update to the application runtime."""

        self._runtime.update(delta_seconds)

    def request_stop(self) -> None:
        """Request the continuous update loop to stop."""

        self._stop_event.set()

    def run(self) -> None:
        """
        Execute the continuous application update loop.

        Updates are paced using a monotonic clock.
        The loop continues until request_stop() is called.
        """

        if self._runtime.state is not RuntimeState.RUNNING:
            raise ModuleRuntimeError(
                "Application must be running before entering the update loop."
            )

        target_interval = 1.0 / self._target_update_rate_hz
        previous_time = perf_counter()

        self._logger.info(
            "Application runtime loop started. Target update rate: %.2f Hz.",
            self._target_update_rate_hz,
        )

        try:
            while not self._stop_event.is_set():
                frame_start = perf_counter()

                delta_seconds = frame_start - previous_time
                previous_time = frame_start

                self.update(delta_seconds)

                elapsed_seconds = perf_counter() - frame_start
                remaining_seconds = target_interval - elapsed_seconds

                if (
                    remaining_seconds > 0
                    and not self._stop_event.is_set()
                ):
                    self._stop_event.wait(remaining_seconds)

        finally:
            self._logger.info(
                "Application runtime loop stopped."
            )

    def stop(self) -> None:
        """Stop the application runtime."""

        self._logger.info("Stopping application.")

        self._runtime.stop()

        self._logger.info("Application stopped.")

    def shutdown(self) -> None:
        """Shut down the application and release its modules."""

        self._logger.info("Shutting down application.")

        self._runtime.shutdown()

        self._logger.info("Application shutdown completed.")
