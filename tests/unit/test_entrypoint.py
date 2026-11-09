
from aditi import __main__ as entrypoint
from aditi.application.runtime.application import Application
from aditi.application.runtime.module_runtime import RuntimeState


class FakeApplication:
    def __init__(self) -> None:
        self.events = []
        self.state = RuntimeState.NEW

    def initialize(self) -> None:
        self.events.append("initialize")
        self.state = RuntimeState.INITIALIZED

    def start(self) -> None:
        self.events.append("start")
        self.state = RuntimeState.RUNNING

    def run(self) -> None:
        self.events.append("run")

    def shutdown(self) -> None:
        self.events.append("shutdown")
        self.state = RuntimeState.SHUTDOWN


def install_fake_application(monkeypatch, application):
    monkeypatch.setattr(
        entrypoint,
        "create_application",
        lambda: application,
    )


def test_create_application_returns_application():
    application = entrypoint.create_application()

    assert isinstance(application, Application)
    assert application.context.application_name == "Aditi"
    assert application.target_update_rate_hz == 60.0


def test_main_executes_application_lifecycle(monkeypatch):
    application = FakeApplication()
    install_fake_application(monkeypatch, application)

    result = entrypoint.main()

    assert result == 0

    assert application.events == [
        "initialize",
        "start",
        "run",
        "shutdown",
    ]

    assert application.state is RuntimeState.SHUTDOWN


def test_main_handles_initialization_failure(monkeypatch):
    application = FakeApplication()

    def fail_initialization():
        application.events.append("initialize")
        raise RuntimeError("Simulated startup failure.")

    application.initialize = fail_initialization

    install_fake_application(monkeypatch, application)

    result = entrypoint.main()

    assert result == 1

    assert application.events == [
        "initialize",
    ]

    assert application.state is RuntimeState.NEW


def test_main_cleans_up_after_failed_initialization_rollback(
    monkeypatch,
):
    application = FakeApplication()

    def fail_initialization():
        application.events.append("initialize")
        application.state = RuntimeState.FAILED
        raise RuntimeError("Simulated initialization failure.")

    application.initialize = fail_initialization

    install_fake_application(monkeypatch, application)

    result = entrypoint.main()

    assert result == 1

    assert application.events == [
        "initialize",
        "shutdown",
    ]

    assert application.state is RuntimeState.SHUTDOWN


def test_main_handles_startup_failure(monkeypatch):
    application = FakeApplication()

    def fail_start():
        application.events.append("start")
        raise RuntimeError("Simulated startup failure.")

    application.start = fail_start

    install_fake_application(monkeypatch, application)

    result = entrypoint.main()

    assert result == 1

    assert application.events == [
        "initialize",
        "start",
        "shutdown",
    ]

    assert application.state is RuntimeState.SHUTDOWN


def test_main_handles_runtime_failure(monkeypatch):
    application = FakeApplication()

    def fail_runtime():
        application.events.append("run")
        raise RuntimeError("Simulated runtime failure.")

    application.run = fail_runtime

    install_fake_application(monkeypatch, application)

    result = entrypoint.main()

    assert result == 1

    assert application.events == [
        "initialize",
        "start",
        "run",
        "shutdown",
    ]


def test_main_handles_keyboard_interrupt(monkeypatch):
    application = FakeApplication()

    def interrupt_runtime():
        application.events.append("run")
        raise KeyboardInterrupt

    application.run = interrupt_runtime

    install_fake_application(monkeypatch, application)

    result = entrypoint.main()

    assert result == 130

    assert application.events == [
        "initialize",
        "start",
        "run",
        "shutdown",
    ]


def test_main_handles_shutdown_failure(monkeypatch):
    application = FakeApplication()

    def fail_shutdown():
        application.events.append("shutdown")
        raise RuntimeError("Simulated shutdown failure.")

    application.shutdown = fail_shutdown

    install_fake_application(monkeypatch, application)

    result = entrypoint.main()

    assert result == 1

    assert application.events == [
        "initialize",
        "start",
        "run",
        "shutdown",
    ]


def test_main_handles_shutdown_interruption(monkeypatch):
    application = FakeApplication()

    def interrupt_shutdown():
        application.events.append("shutdown")
        raise KeyboardInterrupt

    application.shutdown = interrupt_shutdown

    install_fake_application(monkeypatch, application)

    result = entrypoint.main()

    assert result == 130

    assert application.events == [
        "initialize",
        "start",
        "run",
        "shutdown",
    ]
