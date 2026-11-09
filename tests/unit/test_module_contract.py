
import pytest

from aditi.application.modules.base import ApplicationModule
from aditi.application.runtime.context import ApplicationContext


class ExampleModule(ApplicationModule):

    @property
    def module_id(self) -> str:
        return "example"


class DependentModule(ExampleModule):

    @property
    def module_id(self) -> str:
        return "dependent"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ("example",)


def test_module_requires_an_identifier():
    with pytest.raises(TypeError):
        ApplicationModule()


def test_module_has_unique_identifier():
    module = ExampleModule()

    assert module.module_id == "example"


def test_module_has_no_dependencies_by_default():
    module = ExampleModule()

    assert module.dependencies == ()


def test_module_can_declare_dependencies():
    module = DependentModule()

    assert module.dependencies == ("example",)


def test_module_lifecycle_contract():
    module = ExampleModule()
    context = ApplicationContext()

    module.initialize(context)
    module.start()
    module.update(0.016)
    module.stop()
    module.shutdown()
