
from enum import Enum, auto
from math import isfinite

from aditi.application.modules.manager import ModuleManager
from aditi.application.runtime.context import ApplicationContext
from aditi.infrastructure.logging import get_logger

logger = get_logger(__name__)


class RuntimeState(Enum):
    NEW = auto()
    INITIALIZED = auto()
    RUNNING = auto()
    STOPPED = auto()
    FAILED = auto()
    SHUTDOWN = auto()


class ModuleRuntimeError(RuntimeError):
    """Raised when an invalid runtime operation is attempted."""


class ModuleCleanupError(ModuleRuntimeError):
    """
    Raised when one or more ordinary module cleanup operations fail.

    All eligible cleanup operations are attempted before this
    exception is raised. Individual exceptions remain available
    in the errors attribute.
    """

    def __init__(
        self,
        operation: str,
        errors: list[Exception],
    ) -> None:
        self.operation = operation
        self.errors = tuple(errors)

        super().__init__(
            f"{operation.capitalize()} completed with "
            f"{len(self.errors)} cleanup error(s)."
        )


class ModuleRuntime:
    """
    Controls the lifecycle of registered application modules.

    Initialization and startup follow dependency order.
    Stopping and shutdown follow reverse dependency order.

    Cleanup attempts every eligible module, even when an individual
    cleanup operation raises an exception or interruption.

    Failed cleanup operations remain tracked for subsequent retries.

    Interruptions during initialization and startup trigger rollback.
    The original failure is preserved if rollback also fails.
    """

    def __init__(
        self,
        manager: ModuleManager,
        context: ApplicationContext | None = None,
    ) -> None:
        self._manager = manager
        self._context = context or ApplicationContext()

        self._state = RuntimeState.NEW
        self._ordered_modules = ()

        self._initialized_modules = []
        self._started_modules = []

    @property
    def state(self) -> RuntimeState:
        """Return the current runtime state."""

        return self._state

    def initialize(self) -> None:
        """Initialize all registered modules."""

        if self._state is not RuntimeState.NEW:
            raise ModuleRuntimeError(
                "Runtime can only be initialized once."
            )

        logger.info("Initializing application modules.")

        self._ordered_modules = self._manager.resolve_order()

        try:
            for module in self._ordered_modules:
                logger.info(
                    "Initializing module: %s",
                    module.module_id,
                )

                # Track before initialization because initialization
                # may fail after partially acquiring resources.
                self._initialized_modules.append(module)
                module.initialize(self._context)

                logger.info(
                    "Module initialized: %s",
                    module.module_id,
                )

        except BaseException as original_error:
            logger.exception(
                "Module initialization failed. Rolling back initialization."
            )

            cleanup_errors = self._rollback_initialization()

            self._state = (
                RuntimeState.FAILED
                if cleanup_errors
                else RuntimeState.NEW
            )

            self._attach_cleanup_notes(
                original_error,
                cleanup_errors,
                "Initialization rollback",
            )

            # Preserve the original initialization failure.
            raise

        self._state = RuntimeState.INITIALIZED

        logger.info("Application modules initialized successfully.")

    def start(self) -> None:
        """Start all initialized modules."""

        if self._state not in (
            RuntimeState.INITIALIZED,
            RuntimeState.STOPPED,
        ):
            raise ModuleRuntimeError(
                "Runtime must be initialized or stopped before starting."
            )

        if self._started_modules:
            raise ModuleRuntimeError(
                "Pending module cleanup must be completed before starting."
            )

        logger.info("Starting application modules.")

        try:
            for module in self._ordered_modules:
                logger.info(
                    "Starting module: %s",
                    module.module_id,
                )

                # Track before startup because a module may fail
                # after partially activating itself.
                self._started_modules.append(module)
                module.start()

                logger.info(
                    "Module started: %s",
                    module.module_id,
                )

        except BaseException as original_error:
            logger.exception(
                "Module startup failed. Rolling back startup."
            )

            cleanup_errors = self._rollback_start()

            self._state = (
                RuntimeState.FAILED
                if cleanup_errors
                else RuntimeState.INITIALIZED
            )

            self._attach_cleanup_notes(
                original_error,
                cleanup_errors,
                "Startup rollback",
            )

            # Preserve the original startup failure.
            raise

        self._state = RuntimeState.RUNNING

        logger.info("Application runtime is now running.")

    def update(self, delta_seconds: float) -> None:
        """Update all running modules."""

        if self._state is not RuntimeState.RUNNING:
            raise ModuleRuntimeError(
                "Runtime must be running before updating."
            )

        if not isfinite(delta_seconds) or delta_seconds < 0:
            raise ValueError(
                "Delta time must be a finite, non-negative value."
            )

        for module in self._started_modules:
            try:
                module.update(delta_seconds)

            except Exception:
                logger.exception(
                    "Module update failed: %s",
                    module.module_id,
                )
                raise

    def stop(self) -> None:
        """Stop running modules in reverse dependency order."""

        if self._state is not RuntimeState.RUNNING:
            raise ModuleRuntimeError(
                "Runtime must be running before stopping."
            )

        logger.info("Stopping application modules.")

        errors = self._stop_started_modules(
            operation="stop",
        )

        if errors:
            self._state = RuntimeState.FAILED
            self._raise_cleanup_failures("stop", errors)

        self._state = RuntimeState.STOPPED

        logger.info("Application modules stopped.")

    def shutdown(self) -> None:
        """
        Release initialized modules in reverse dependency order.

        Shutdown attempts all remaining cleanup operations, including
        when stopping or shutting down an individual module is interrupted.

        Failed modules remain tracked for a subsequent cleanup attempt.
        """

        if self._state is RuntimeState.SHUTDOWN:
            return

        if self._state is RuntimeState.NEW:
            raise ModuleRuntimeError(
                "Runtime must be initialized before shutdown."
            )

        errors: list[BaseException] = []

        if self._started_modules:
            logger.info(
                "Stopping remaining active modules before shutdown."
            )

            errors.extend(
                self._stop_started_modules(
                    operation="shutdown stop",
                )
            )

        logger.info("Shutting down application modules.")

        failed_modules = []

        for module in reversed(self._initialized_modules):
            logger.info(
                "Shutting down module: %s",
                module.module_id,
            )

            try:
                module.shutdown()

            except BaseException as error:
                logger.exception(
                    "Module shutdown failed: %s",
                    module.module_id,
                )

                errors.append(error)
                failed_modules.append(module)

            else:
                logger.info(
                    "Module shutdown completed: %s",
                    module.module_id,
                )

        failed_module_ids = {
            id(module)
            for module in failed_modules
        }

        # Retain only modules whose shutdown did not complete.
        self._initialized_modules = list(
            reversed(failed_modules)
        )

        # A successful shutdown completes the module's lifecycle,
        # even if its preceding stop operation failed.
        self._started_modules = [
            module
            for module in self._started_modules
            if id(module) in failed_module_ids
        ]

        self._state = (
            RuntimeState.FAILED
            if self._initialized_modules
            else RuntimeState.SHUTDOWN
        )

        if errors:
            self._raise_cleanup_failures(
                "shutdown",
                errors,
            )

        logger.info("Application runtime shutdown completed.")

    def _stop_started_modules(
        self,
        operation: str,
    ) -> list[BaseException]:
        """
        Attempt to stop every tracked module.

        Successfully stopped modules are removed from tracking.
        Failed modules remain tracked for another cleanup attempt.
        """

        errors: list[BaseException] = []
        failed_module_ids = set()

        for module in reversed(self._started_modules):
            logger.info(
                "Stopping module: %s",
                module.module_id,
            )

            try:
                module.stop()

            except BaseException as error:
                logger.exception(
                    "Module stop failed during %s: %s",
                    operation,
                    module.module_id,
                )

                errors.append(error)
                failed_module_ids.add(id(module))

            else:
                logger.info(
                    "Module stopped: %s",
                    module.module_id,
                )

        self._started_modules = [
            module
            for module in self._started_modules
            if id(module) in failed_module_ids
        ]

        return errors

    def _rollback_start(self) -> list[BaseException]:
        """Stop modules that started or partially started before failure."""

        logger.warning("Rolling back started modules.")

        return self._stop_started_modules(
            operation="startup rollback",
        )

    def _rollback_initialization(self) -> list[BaseException]:
        """
        Shut down modules that initialized or partially initialized.

        Successful cleanup is removed from tracking. Failed cleanup
        remains tracked for a subsequent shutdown attempt.
        """

        logger.warning("Rolling back initialized modules.")

        errors: list[BaseException] = []
        failed_modules = []

        for module in reversed(self._initialized_modules):
            try:
                module.shutdown()

            except BaseException as error:
                logger.exception(
                    "Module initialization rollback failed: %s",
                    module.module_id,
                )

                errors.append(error)
                failed_modules.append(module)

        self._initialized_modules = list(
            reversed(failed_modules)
        )

        return errors

    @staticmethod
    def _attach_cleanup_notes(
        original_error: BaseException,
        cleanup_errors: list[BaseException],
        operation: str,
    ) -> None:
        """
        Attach cleanup failures to the original lifecycle exception.

        The original exception remains the primary failure.
        """

        for cleanup_error in cleanup_errors:
            original_error.add_note(
                f"{operation} also failed with "
                f"{type(cleanup_error).__name__}: {cleanup_error}"
            )

    @staticmethod
    def _raise_cleanup_failures(
        operation: str,
        errors: list[BaseException],
    ) -> None:
        """
        Propagate interruptions after all cleanup attempts.

        Interruptions take precedence over ordinary cleanup errors.
        Remaining errors are attached as diagnostic notes.
        """

        if not errors:
            return

        interruptions = [
            error
            for error in errors
            if not isinstance(error, Exception)
        ]

        if interruptions:
            primary_error = interruptions[0]

            for error in errors:
                if error is primary_error:
                    continue

                primary_error.add_note(
                    f"{operation.capitalize()} also encountered "
                    f"{type(error).__name__}: {error}"
                )

            raise primary_error

        ordinary_errors = [
            error
            for error in errors
            if isinstance(error, Exception)
        ]

        raise ModuleCleanupError(
            operation=operation,
            errors=ordinary_errors,
        )
