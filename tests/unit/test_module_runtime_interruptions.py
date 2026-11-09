
import pytest

from aditi.application.modules.base import ApplicationModule
from aditi.application.modules.manager import ModuleManager
from aditi.application.runtime.context import ApplicationContext
from aditi.application.runtime.module_runtime import (
    ModuleRuntime,
    RuntimeState,
)


class InterruptibleModule(ApplicationModule):
    def __init__(
        self,
        identifier: str,
        events: list[str],
        dependencies: tuple[str, ...] = (),
    ) -> None:
        self._identifier = identifier
        self._events = events
        self._dependencies = dependencies

        self.interrupt_initialize = False
        self.interrupt_start = False
        self.interrupt_stop = False
        self.interrupt_shutdown = False

    @property
    def module_id(self) -> str:
        return self._identifier

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._dependencies

    def initialize(self, context: ApplicationContext) -> None:
        self._events.append(f"{self.module_id}:initialize")

        if self.interrupt_initialize:
            raise KeyboardInterrupt("initialization interrupted")

    def start(self) -> None:
        self._events.append(f"{self.module_id}:start")

        if self.interrupt_start:
            raise KeyboardInterrupt("startup interrupted")

    def update(self, delta_seconds: float) -> None:
        self._events.append(f"{self.module_id}:update")

    def stop(self) -> None:
        self._events.append(f"{self.module_id}:stop")

        if self.interrupt_stop:
            self.interrupt_stop = False
            raise KeyboardInterrupt("stop interrupted")

    def shutdown(self) -> None:
        self._events.append(f"{self.module_id}:shutdown")

        if self.interrupt_shutdown:
            self.interrupt_shutdown = False
            raise KeyboardInterrupt("shutdown interrupted")


def create_runtime(
    module_a: InterruptibleModule,
    module_b: InterruptibleModule,
) -> ModuleRuntime:
    manager = ModuleManager()

    manager.register(module_b)
    manager.register(module_a)

    return ModuleRuntime(manager)


def test_initialization_preserves_original_interruption_during_rollback():
    events = []

    module_a = InterruptibleModule("module_a", events)
    module_b = InterruptibleModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    module_b.interrupt_initialize = True
    module_b.interrupt_shutdown = True

    runtime = create_runtime(module_a, module_b)

    with pytest.raises(
        KeyboardInterrupt,
        match="initialization interrupted",
    ) as error_info:
        runtime.initialize()

    assert runtime.state is RuntimeState.FAILED

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    assert any(
        "Initialization rollback also failed" in note
        for note in error_info.value.__notes__
    )

    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
        "module_b:shutdown",
    ]


def test_startup_preserves_original_interruption_during_rollback():
    events = []

    module_a = InterruptibleModule("module_a", events)
    module_b = InterruptibleModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    module_a.interrupt_stop = True
    module_b.interrupt_start = True

    runtime = create_runtime(module_a, module_b)
    runtime.initialize()

    with pytest.raises(
        KeyboardInterrupt,
        match="startup interrupted",
    ) as error_info:
        runtime.start()

    assert runtime.state is RuntimeState.FAILED

    assert events[-4:] == [
        "module_a:start",
        "module_b:start",
        "module_b:stop",
        "module_a:stop",
    ]

    assert any(
        "Startup rollback also failed" in note
        for note in error_info.value.__notes__
    )

    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events[-3:] == [
        "module_a:stop",
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    assert events.count("module_a:stop") == 2
    assert events.count("module_b:stop") == 1


def test_stop_interruption_does_not_prevent_other_modules_from_stopping():
    events = []

    module_a = InterruptibleModule("module_a", events)
    module_b = InterruptibleModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    module_b.interrupt_stop = True

    runtime = create_runtime(module_a, module_b)
    runtime.initialize()
    runtime.start()

    with pytest.raises(
        KeyboardInterrupt,
        match="stop interrupted",
    ):
        runtime.stop()

    assert runtime.state is RuntimeState.FAILED

    assert events[-2:] == [
        "module_b:stop",
        "module_a:stop",
    ]

    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events[-3:] == [
        "module_b:stop",
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    assert events.count("module_a:stop") == 1
    assert events.count("module_b:stop") == 2


def test_shutdown_interruption_does_not_prevent_other_modules_from_shutting_down():
    events = []

    module_a = InterruptibleModule("module_a", events)
    module_b = InterruptibleModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    module_b.interrupt_shutdown = True

    runtime = create_runtime(module_a, module_b)
    runtime.initialize()

    with pytest.raises(
        KeyboardInterrupt,
        match="shutdown interrupted",
    ):
        runtime.shutdown()

    assert runtime.state is RuntimeState.FAILED

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN

    assert events == [
        "module_a:initialize",
        "module_b:initialize",
        "module_b:shutdown",
        "module_a:shutdown",
        "module_b:shutdown",
    ]


def test_shutdown_continues_after_interrupted_stop():
    events = []

    module_a = InterruptibleModule("module_a", events)
    module_b = InterruptibleModule(
        "module_b",
        events,
        dependencies=("module_a",),
    )

    module_b.interrupt_stop = True

    runtime = create_runtime(module_a, module_b)
    runtime.initialize()
    runtime.start()

    with pytest.raises(
        KeyboardInterrupt,
        match="stop interrupted",
    ):
        runtime.shutdown()

    assert events[-4:] == [
        "module_b:stop",
        "module_a:stop",
        "module_b:shutdown",
        "module_a:shutdown",
    ]

    assert runtime.state is RuntimeState.SHUTDOWN

    runtime.shutdown()

    assert events.count("module_a:shutdown") == 1
    assert events.count("module_b:shutdown") == 1
