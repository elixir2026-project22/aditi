
import logging

import pytest

from aditi.application.modules.base import ApplicationModule
from aditi.application.modules.manager import ModuleManager
from aditi.application.runtime.application import Application
from aditi.application.runtime.context import ApplicationContext
from aditi.application.runtime.module_runtime import (
    ModuleCleanupError,
    RuntimeState,
)
from aditi.infrastructure.logging import LoggingConfig


class IntegrationModule(ApplicationModule):
    def __init__(
        self,
        identifier: str,
        events: list[str],
        dependencies: tuple[str, ...] = (),
    ) -> None:
        self._identifier = identifier
        self._events = events
        self._dependencies = dependencies
        self.received_context = None

    @property
    def module_id(self) -> str:
        return self._identifier

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._dependencies

    def initialize(self, context: ApplicationContext) -> None:
        self.received_context = context
        self._events.append(f"{self.module_id}:initialize")

    def start(self) -> None:
        self._events.append(f"{self.module_id}:start")

    def update(self, delta_seconds: float) -> None:
        self._events.append(f"{self.module_id}:update")

    def stop(self) -> None:
        self._events.append(f"{self.module_id}:stop")

    def shutdown(self) -> None:
        self._events.append(f"{self.module_id}:shutdown")


class FailingShutdownIntegrationModule(IntegrationModule):
    def __init__(
        self,
        identifier: str,
        events: list[str],
        dependencies: tuple[str, ...] = (),
    ) -> None:
        super().__init__(identifier, events, dependencies)
        self.fail_shutdown = True

    def shutdown(self) -> None:
        self._events.append(f"{self.module_id}:shutdown")

        if self.fail_shutdown:
            raise RuntimeError("Simulated integration shutdown failure.")


class InterruptedInitializationIntegrationModule(IntegrationModule):
    def initialize(self, context: ApplicationContext) -> None:
        self.received_context = context
        self._events.append(f"{self.module_id}:initialize")
        raise KeyboardInterrupt


class InterruptedStartIntegrationModule(IntegrationModule):
    def start(self) -> None:
        self._events.append(f"{self.module_id}:start")
        raise KeyboardInterrupt


class InterruptedUpdateIntegrationModule(IntegrationModule):
    def update(self, delta_seconds: float) -> None:
        self._events.append(f"{self.module_id}:update")
        raise KeyboardInterrupt


class StopFailsOnceIntegrationModule(IntegrationModule):
    def __init__(
        self,
        identifier: str,
        events: list[str],
        dependencies: tuple[str, ...] = (),
    ) -> None:
        super().__init__(identifier, events, dependencies)
        self.stop_attempts = 0

    def stop(self) -> None:
        self._events.append(f"{self.module_id}:stop")
        self.stop_attempts += 1

        if self.stop_attempts == 1:
            raise RuntimeError("Simulated integration stop failure.")


def create_application_with_modules(
    context: ApplicationContext | None = None,
):
    events = []
    manager = ModuleManager()

    module_a = IntegrationModule(
        "module_a",
        events,
    )

    module_b = IntegrationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    # Register in reverse order to verify dependency resolution.
    manager.register(module_b)
    manager.register(module_a)

    application = Application(
        module_manager=manager,
        context=context,
        logging_config=LoggingConfig(
            level=logging.CRITICAL,
        ),
    )

    return application, events, module_a, module_b


def test_application_integrates_complete_module_lifecycle():
    application, events, _, _ = create_application_with_modules()

    application.initialize()
    application.start()
    application.update(0.016)
    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_a:start",
        "module_b:start",
        "module_a:update",
        "module_b:update",
        "module_b:stop",
        "module_a:stop",
        "module_b:shutdown",
        "module_a:shutdown",
    ]


def test_application_shares_context_with_all_modules():
    context = ApplicationContext(
        application_name="Aditi Integration Test",
        config={
            "environment": "test",
            "debug": True,
        },
    )

    application, _, module_a, module_b = (
        create_application_with_modules(context)
    )

    application.initialize()

    assert module_a.received_context is context
    assert module_b.received_context is context

    assert application.context is context

    application.shutdown()


def test_application_shutdown_after_explicit_stop():
    application, events, _, _ = create_application_with_modules()

    application.initialize()
    application.start()
    application.stop()
    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN

    assert events.count("module_a:stop") == 1
    assert events.count("module_b:stop") == 1


def test_application_retries_failed_module_cleanup():
    events = []
    manager = ModuleManager()

    module_a = IntegrationModule(
        "module_a",
        events,
    )

    module_b = FailingShutdownIntegrationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    application = Application(
        module_manager=manager,
        logging_config=LoggingConfig(
            level=logging.CRITICAL,
        ),
    )

    application.initialize()

    with pytest.raises(ModuleCleanupError):
        application.shutdown()

    assert application.state is RuntimeState.FAILED

    # Allow the failed module to clean up on retry.
    module_b.fail_shutdown = False

    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
        "module_b:shutdown",
    ]


def test_application_rolls_back_interrupted_initialization():
    events = []
    manager = ModuleManager()

    module_a = IntegrationModule(
        "module_a",
        events,
    )

    module_b = InterruptedInitializationIntegrationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    application = Application(
        module_manager=manager,
        logging_config=LoggingConfig(
            level=logging.CRITICAL,
        ),
    )

    with pytest.raises(KeyboardInterrupt):
        application.initialize()

    assert application.state is RuntimeState.NEW

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
    ]


def test_application_rolls_back_interrupted_startup():
    events = []
    manager = ModuleManager()

    module_a = IntegrationModule(
        "module_a",
        events,
    )

    module_b = InterruptedStartIntegrationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    application = Application(
        module_manager=manager,
        logging_config=LoggingConfig(
            level=logging.CRITICAL,
        ),
    )

    application.initialize()

    with pytest.raises(KeyboardInterrupt):
        application.start()

    assert application.state is RuntimeState.INITIALIZED

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_a:start",
        "module_b:start",
        "module_b:stop",
        "module_a:stop",
    ]

    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN

    assert events[-2:] == [
        "module_b:shutdown",
        "module_a:shutdown",
    ]


def test_application_update_loop_propagates_keyboard_interrupt():
    events = []
    manager = ModuleManager()

    module_a = IntegrationModule(
        "module_a",
        events,
    )

    module_b = InterruptedUpdateIntegrationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    application = Application(
        module_manager=manager,
        logging_config=LoggingConfig(
            level=logging.CRITICAL,
        ),
    )

    application.initialize()
    application.start()

    with pytest.raises(KeyboardInterrupt):
        application.run()

    # The runtime remains running until the bootstrap performs shutdown.
    assert application.state is RuntimeState.RUNNING

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_a:start",
        "module_b:start",
        "module_a:update",
        "module_b:update",
    ]

    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN

    assert events[-4:] == [
        "module_b:stop",
        "module_a:stop",
        "module_b:shutdown",
        "module_a:shutdown",
    ]


def test_application_retries_failed_startup_rollback_during_shutdown():
    events = []
    manager = ModuleManager()

    module_a = StopFailsOnceIntegrationModule(
        "module_a",
        events,
    )

    module_b = InterruptedStartIntegrationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    application = Application(
        module_manager=manager,
        logging_config=LoggingConfig(
            level=logging.CRITICAL,
        ),
    )

    application.initialize()

    with pytest.raises(KeyboardInterrupt):
        application.start()

    assert application.state is RuntimeState.FAILED

    # Shutdown retries the stop operation that failed during rollback.
    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN
    assert module_a.stop_attempts == 2

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_a:start",
        "module_b:start",
        "module_b:stop",
        "module_a:stop",
        "module_a:stop",
        "module_b:shutdown",
        "module_a:shutdown",
    ]
