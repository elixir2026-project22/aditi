
import logging

import pytest

from aditi.application.modules.base import ApplicationModule
from aditi.application.modules.manager import ModuleManager
from aditi.application.runtime.context import ApplicationContext
from aditi.application.runtime.module_runtime import (
    ModuleCleanupError,
    ModuleRuntime,
    ModuleRuntimeError,
    RuntimeState,
)


@pytest.fixture
def runtime_caplog(caplog):
    logger = logging.getLogger("aditi")
    previous_level = logger.level
    previous_propagate = logger.propagate

    logger.setLevel(logging.DEBUG)
    logger.propagate = True

    yield caplog

    logger.setLevel(previous_level)
    logger.propagate = previous_propagate


class RecordingModule(ApplicationModule):
    def __init__(
        self,
        identifier: str,
        events: list[str],
        dependencies: tuple[str, ...] = (),
    ) -> None:
        self._identifier = identifier
        self._events = events
        self._dependencies = dependencies

    @property
    def module_id(self) -> str:
        return self._identifier

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._dependencies

    def initialize(self, context: ApplicationContext) -> None:
        self._events.append(f"{self.module_id}:initialize")

    def start(self) -> None:
        self._events.append(f"{self.module_id}:start")

    def update(self, delta_seconds: float) -> None:
        self._events.append(f"{self.module_id}:update")

    def stop(self) -> None:
        self._events.append(f"{self.module_id}:stop")

    def shutdown(self) -> None:
        self._events.append(f"{self.module_id}:shutdown")


class FailingUpdateModule(RecordingModule):
    def update(self, delta_seconds: float) -> None:
        self._events.append(f"{self.module_id}:update")
        raise RuntimeError("Simulated update failure.")


class FailingInitializationModule(RecordingModule):
    def initialize(self, context: ApplicationContext) -> None:
        self._events.append(f"{self.module_id}:initialize")
        raise RuntimeError("Simulated initialization failure.")


class FailingStartModule(RecordingModule):
    def start(self) -> None:
        self._events.append(f"{self.module_id}:start")
        raise RuntimeError("Simulated startup failure.")


class InterruptedInitializationModule(RecordingModule):
    def initialize(self, context: ApplicationContext) -> None:
        self._events.append(f"{self.module_id}:initialize")
        raise KeyboardInterrupt


class InterruptedStartModule(RecordingModule):
    def start(self) -> None:
        self._events.append(f"{self.module_id}:start")
        raise KeyboardInterrupt


class StopFailsOnceModule(RecordingModule):
    def __init__(
        self,
        identifier: str,
        events: list[str],
    ) -> None:
        super().__init__(identifier, events)
        self._stop_attempts = 0

    def stop(self) -> None:
        self._events.append(f"{self.module_id}:stop")
        self._stop_attempts += 1

        if self._stop_attempts == 1:
            raise RuntimeError("Simulated stop failure.")


class ShutdownFailsModule(RecordingModule):
    def shutdown(self) -> None:
        self._events.append(f"{self.module_id}:shutdown")
        raise RuntimeError("Simulated shutdown failure.")


def create_runtime():
    events = []
    manager = ModuleManager()

    module_a = RecordingModule(
        "module_a",
        events,
    )

    module_b = RecordingModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)

    return runtime, events


def test_runtime_initialization():
    runtime, events = create_runtime()

    runtime.initialize()

    assert runtime.state is RuntimeState.INITIALIZED

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
    ]


def test_runtime_start():
    runtime, events = create_runtime()

    runtime.initialize()
    runtime.start()

    assert runtime.state is RuntimeState.RUNNING

    assert events[-2:] == [
        "module_a:start",
        "module_b:start",
    ]


def test_runtime_update():
    runtime, events = create_runtime()

    runtime.initialize()
    runtime.start()
    runtime.update(0.016)

    assert events[-2:] == [
        "module_a:update",
        "module_b:update",
    ]


def test_runtime_stop_uses_reverse_order():
    runtime, events = create_runtime()

    runtime.initialize()
    runtime.start()
    runtime.stop()

    assert runtime.state is RuntimeState.STOPPED

    assert events[-2:] == [
        "module_b:stop",
        "module_a:stop",
    ]


def test_runtime_shutdown_uses_reverse_order():
    runtime, events = create_runtime()

    runtime.initialize()
    runtime.start()
    runtime.stop()
    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events[-2:] == [
        "module_b:shutdown",
        "module_a:shutdown",
    ]


def test_shutdown_automatically_stops_running_modules():
    runtime, events = create_runtime()

    runtime.initialize()
    runtime.start()
    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events[-4:] == [
        "module_b:stop",
        "module_a:stop",
        "module_b:shutdown",
        "module_a:shutdown",
    ]


def test_runtime_rejects_update_before_start():
    runtime, _ = create_runtime()

    runtime.initialize()

    with pytest.raises(ModuleRuntimeError):
        runtime.update(0.016)


def test_runtime_rejects_invalid_delta_time():
    runtime, _ = create_runtime()

    runtime.initialize()
    runtime.start()

    with pytest.raises(ValueError):
        runtime.update(-0.016)

    with pytest.raises(ValueError):
        runtime.update(float("inf"))


def test_runtime_can_restart_after_stop():
    runtime, events = create_runtime()

    runtime.initialize()
    runtime.start()
    runtime.stop()
    runtime.start()

    assert runtime.state is RuntimeState.RUNNING

    assert events[-2:] == [
        "module_a:start",
        "module_b:start",
    ]


# ---------------------------------------------------------
# Initialization and startup rollback tests
# ---------------------------------------------------------


def test_initialization_failure_cleans_up_failing_module():
    events = []
    manager = ModuleManager()

    module_a = RecordingModule(
        "module_a",
        events,
    )

    module_b = FailingInitializationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)

    with pytest.raises(
        RuntimeError,
        match="Simulated initialization failure",
    ):
        runtime.initialize()

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    assert runtime.state is RuntimeState.NEW


def test_initialization_rollback_continues_after_cleanup_failure():
    events = []
    manager = ModuleManager()

    class FailingCleanupModule(RecordingModule):
        def __init__(self, identifier, events):
            super().__init__(identifier, events)
            self.fail_cleanup = True

        def shutdown(self):
            self._events.append(f"{self.module_id}:shutdown")

            if self.fail_cleanup:
                raise RuntimeError("Simulated cleanup failure.")

    module_a = FailingCleanupModule(
        "module_a",
        events,
    )

    module_b = FailingInitializationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)

    with pytest.raises(
        RuntimeError,
        match="Simulated initialization failure",
    ):
        runtime.initialize()

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    assert runtime.state is RuntimeState.FAILED

    module_a.fail_cleanup = False
    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events[-1] == "module_a:shutdown"


def test_start_failure_rolls_back_failing_and_started_modules():
    events = []
    manager = ModuleManager()

    module_a = RecordingModule(
        "module_a",
        events,
    )

    module_b = FailingStartModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)
    runtime.initialize()

    with pytest.raises(
        RuntimeError,
        match="Simulated startup failure",
    ):
        runtime.start()

    assert events[-4:] == [
        "module_a:start",
        "module_b:start",
        "module_b:stop",
        "module_a:stop",
    ]

    assert runtime.state is RuntimeState.INITIALIZED


def test_start_rollback_retains_modules_when_cleanup_fails():
    events = []
    manager = ModuleManager()

    module_a = StopFailsOnceModule(
        "module_a",
        events,
    )

    module_b = FailingStartModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)
    runtime.initialize()

    with pytest.raises(
        RuntimeError,
        match="Simulated startup failure",
    ):
        runtime.start()

    assert runtime.state is RuntimeState.FAILED

    with pytest.raises(ModuleRuntimeError):
        runtime.start()

    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events.count("module_a:stop") == 2


def test_interrupted_initialization_rolls_back_and_reraises():
    events = []
    manager = ModuleManager()

    module_a = RecordingModule(
        "module_a",
        events,
    )

    module_b = InterruptedInitializationModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)

    with pytest.raises(KeyboardInterrupt):
        runtime.initialize()

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    assert runtime.state is RuntimeState.NEW


def test_interrupted_start_rolls_back_and_reraises():
    events = []
    manager = ModuleManager()

    module_a = RecordingModule(
        "module_a",
        events,
    )

    module_b = InterruptedStartModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)
    runtime.initialize()

    with pytest.raises(KeyboardInterrupt):
        runtime.start()

    assert events[-4:] == [
        "module_a:start",
        "module_b:start",
        "module_b:stop",
        "module_a:stop",
    ]

    assert runtime.state is RuntimeState.INITIALIZED


def test_interrupted_initialization_retains_failed_cleanup_for_retry():
    events = []
    manager = ModuleManager()

    class InterruptedAndCleanupFailsModule(RecordingModule):
        def __init__(self, identifier, events):
            super().__init__(identifier, events)
            self.fail_cleanup = True

        def initialize(self, context):
            self._events.append(f"{self.module_id}:initialize")
            raise KeyboardInterrupt

        def shutdown(self):
            self._events.append(f"{self.module_id}:shutdown")

            if self.fail_cleanup:
                raise RuntimeError("Simulated cleanup failure.")

    module = InterruptedAndCleanupFailsModule(
        "module_a",
        events,
    )

    manager.register(module)

    runtime = ModuleRuntime(manager)

    with pytest.raises(KeyboardInterrupt):
        runtime.initialize()

    assert runtime.state is RuntimeState.FAILED

    assert events == [
        "module_a:initialize",
        "module_a:shutdown",
    ]

    module.fail_cleanup = False
    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events == [
        "module_a:initialize",
        "module_a:shutdown",
        "module_a:shutdown",
    ]


# ---------------------------------------------------------
# Stop and shutdown failure tests
# ---------------------------------------------------------


def test_stop_attempts_all_modules_when_one_fails():
    events = []
    manager = ModuleManager()

    module_a = RecordingModule(
        "module_a",
        events,
    )

    module_b = StopFailsOnceModule(
        "module_b",
        events,
    )

    module_b._dependencies = ("module_a",)

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)
    runtime.initialize()
    runtime.start()

    with pytest.raises(ModuleCleanupError) as error_info:
        runtime.stop()

    assert len(error_info.value.errors) == 1
    assert error_info.value.operation == "stop"

    assert events[-2:] == [
        "module_b:stop",
        "module_a:stop",
    ]

    assert runtime.state is RuntimeState.FAILED


def test_shutdown_retries_failed_stop_and_cleans_all_modules():
    events = []
    manager = ModuleManager()

    module_a = RecordingModule(
        "module_a",
        events,
    )

    module_b = StopFailsOnceModule(
        "module_b",
        events,
    )

    module_b._dependencies = ("module_a",)

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)
    runtime.initialize()
    runtime.start()

    with pytest.raises(ModuleCleanupError):
        runtime.stop()

    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events[-4:] == [
        "module_a:stop",
        "module_b:stop",
        "module_b:shutdown",
        "module_a:shutdown",
    ]


def test_shutdown_attempts_all_modules_after_shutdown_failure():
    events = []
    manager = ModuleManager()

    module_a = RecordingModule(
        "module_a",
        events,
    )

    module_b = ShutdownFailsModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    manager.register(module_b)
    manager.register(module_a)

    runtime = ModuleRuntime(manager)
    runtime.initialize()

    with pytest.raises(ModuleCleanupError) as error_info:
        runtime.shutdown()

    assert len(error_info.value.errors) == 1
    assert error_info.value.operation == "shutdown"

    assert events[-2:] == [
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    assert runtime.state is RuntimeState.FAILED


def test_shutdown_can_retry_failed_module_cleanup():
    events = []
    manager = ModuleManager()

    class ShutdownFailsOnceModule(RecordingModule):
        def __init__(self, identifier, events):
            super().__init__(identifier, events)
            self.fail_cleanup = True

        def shutdown(self):
            self._events.append(f"{self.module_id}:shutdown")

            if self.fail_cleanup:
                self.fail_cleanup = False
                raise RuntimeError("Simulated shutdown failure.")

    module = ShutdownFailsOnceModule(
        "module_a",
        events,
    )

    manager.register(module)

    runtime = ModuleRuntime(manager)
    runtime.initialize()

    with pytest.raises(ModuleCleanupError):
        runtime.shutdown()

    assert runtime.state is RuntimeState.FAILED

    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events == [
        "module_a:initialize",
        "module_a:shutdown",
        "module_a:shutdown",
    ]


# ---------------------------------------------------------
# Runtime logging tests
# ---------------------------------------------------------


def test_runtime_logs_module_initialization(runtime_caplog):
    runtime, _ = create_runtime()

    runtime.initialize()

    messages = [
        record.getMessage()
        for record in runtime_caplog.records
    ]

    assert "Initializing application modules." in messages

    assert "Initializing module: module_a" in messages
    assert "Module initialized: module_a" in messages

    assert "Initializing module: module_b" in messages
    assert "Module initialized: module_b" in messages

    assert "Application modules initialized successfully." in messages


def test_runtime_logs_complete_lifecycle(runtime_caplog):
    runtime, _ = create_runtime()

    runtime.initialize()
    runtime.start()
    runtime.stop()
    runtime.shutdown()

    messages = [
        record.getMessage()
        for record in runtime_caplog.records
    ]

    assert "Starting application modules." in messages
    assert "Module started: module_a" in messages
    assert "Module started: module_b" in messages

    assert "Stopping application modules." in messages
    assert "Module stopped: module_b" in messages
    assert "Module stopped: module_a" in messages

    assert "Shutting down application modules." in messages
    assert "Module shutdown completed: module_b" in messages
    assert "Module shutdown completed: module_a" in messages

    assert "Application runtime shutdown completed." in messages


def test_runtime_logs_update_failure_with_traceback(runtime_caplog):
    events = []
    manager = ModuleManager()

    module = FailingUpdateModule(
        "failing_module",
        events,
    )

    manager.register(module)

    runtime = ModuleRuntime(manager)

    runtime.initialize()
    runtime.start()

    with pytest.raises(RuntimeError):
        runtime.update(0.016)

    error_records = [
        record
        for record in runtime_caplog.records
        if record.getMessage() == (
            "Module update failed: failing_module"
        )
    ]

    assert len(error_records) == 1
    assert error_records[0].levelno == logging.ERROR
    assert error_records[0].exc_info is not None

    assert error_records[0].name == (
        "aditi.application.runtime.module_runtime"
    )


def test_runtime_logs_initialization_failure(runtime_caplog):
    events = []
    manager = ModuleManager()

    manager.register(
        FailingInitializationModule(
            "failing_module",
            events,
        )
    )

    runtime = ModuleRuntime(manager)

    with pytest.raises(RuntimeError):
        runtime.initialize()

    error_records = [
        record
        for record in runtime_caplog.records
        if record.getMessage() == (
            "Module initialization failed. Rolling back initialization."
        )
    ]

    assert len(error_records) == 1
    assert error_records[0].levelno == logging.ERROR
    assert error_records[0].exc_info is not None

    warning_messages = [
        record.getMessage()
        for record in runtime_caplog.records
        if record.levelno == logging.WARNING
    ]

    assert "Rolling back initialized modules." in warning_messages
