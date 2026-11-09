
import logging

import pytest

from aditi.application.modules.base import ApplicationModule
from aditi.application.modules.manager import ModuleManager
from aditi.application.runtime.application import Application
from aditi.application.runtime.context import ApplicationContext
from aditi.application.runtime.module_runtime import (
    ModuleRuntimeError,
    RuntimeState,
)
from aditi.infrastructure.logging import LoggingConfig


class RecordingModule(ApplicationModule):

    def __init__(self) -> None:
        self.events = []

    @property
    def module_id(self) -> str:
        return "test_module"

    def initialize(self, context: ApplicationContext) -> None:
        self.events.append("initialize")

    def start(self) -> None:
        self.events.append("start")

    def update(self, delta_seconds: float) -> None:
        self.events.append("update")

    def stop(self) -> None:
        self.events.append("stop")

    def shutdown(self) -> None:
        self.events.append("shutdown")


def create_application(
    context: ApplicationContext | None = None,
    target_update_rate_hz: float = 60.0,
) -> tuple[Application, RecordingModule]:
    manager = ModuleManager()

    module = RecordingModule()

    manager.register(module)

    application = Application(
        module_manager=manager,
        context=context,
        logging_config=LoggingConfig(
            level=logging.CRITICAL,
        ),
        target_update_rate_hz=target_update_rate_hz,
    )

    return application, module


def test_application_starts_in_new_state():
    application, _ = create_application()

    assert application.state is RuntimeState.NEW


def test_application_initialization():
    application, module = create_application()

    application.initialize()

    assert application.state is RuntimeState.INITIALIZED

    assert module.events == [
        "initialize",
    ]


def test_application_complete_lifecycle():
    application, module = create_application()

    application.initialize()
    application.start()
    application.update(0.016)
    application.stop()
    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN

    assert module.events == [
        "initialize",
        "start",
        "update",
        "stop",
        "shutdown",
    ]


def test_application_uses_provided_context():
    context = ApplicationContext(
        application_name="Aditi Test",
        config={"environment": "testing"},
    )

    application, _ = create_application(context)

    assert application.context is context
    assert application.context.application_name == "Aditi Test"


def test_application_rejects_start_before_initialization():
    application, _ = create_application()

    with pytest.raises(ModuleRuntimeError):
        application.start()


def test_application_can_shutdown_after_initialization():
    application, module = create_application()

    application.initialize()
    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN

    assert module.events == [
        "initialize",
        "shutdown",
    ]


def test_application_shutdown_is_idempotent():
    application, module = create_application()

    application.initialize()
    application.shutdown()
    application.shutdown()

    assert application.state is RuntimeState.SHUTDOWN

    assert module.events == [
        "initialize",
        "shutdown",
    ]


def test_application_rejects_invalid_update_rates():
    invalid_rates = [
        0,
        -1,
        float("inf"),
        float("-inf"),
        float("nan"),
    ]

    manager = ModuleManager()

    for rate in invalid_rates:
        with pytest.raises(ValueError):
            Application(
                module_manager=manager,
                target_update_rate_hz=rate,
            )


def test_application_exposes_target_update_rate():
    application, _ = create_application(
        target_update_rate_hz=30.0,
    )

    assert application.target_update_rate_hz == 30.0


def test_application_run_requires_running_state():
    application, _ = create_application()

    application.initialize()

    with pytest.raises(ModuleRuntimeError):
        application.run()


def test_application_run_updates_until_stop_requested(monkeypatch):
    application, module = create_application(
        target_update_rate_hz=1_000_000.0,
    )

    application.initialize()
    application.start()

    updates = []

    def update_and_request_stop(delta_seconds: float) -> None:
        updates.append(delta_seconds)

        if len(updates) == 3:
            application.request_stop()

    monkeypatch.setattr(
        application,
        "update",
        update_and_request_stop,
    )

    application.run()

    assert len(updates) == 3
    assert all(delta >= 0 for delta in updates)

    assert application.state is RuntimeState.RUNNING

    application.shutdown()

    assert module.events == [
        "initialize",
        "start",
        "stop",
        "shutdown",
    ]


def test_application_request_stop_ends_runtime_loop():
    application, module = create_application(
        target_update_rate_hz=60.0,
    )

    application.initialize()
    application.start()

    application.request_stop()
    application.run()

    assert application.state is RuntimeState.RUNNING

    application.shutdown()

    assert module.events == [
        "initialize",
        "start",
        "stop",
        "shutdown",
    ]
