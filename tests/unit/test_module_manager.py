
import pytest

from aditi.application.modules.base import ApplicationModule
from aditi.application.modules.manager import (
    ModuleManager,
    ModuleManagerError,
)


class ExampleModule(ApplicationModule):

    def __init__(
        self,
        identifier: str,
        dependencies: tuple[str, ...] = (),
    ) -> None:
        self._identifier = identifier
        self._dependencies = dependencies

    @property
    def module_id(self) -> str:
        return self._identifier

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._dependencies


def test_register_module():
    manager = ModuleManager()
    module = ExampleModule("example")

    manager.register(module)

    assert manager.get("example") is module


def test_prevent_duplicate_registration():
    manager = ModuleManager()

    manager.register(ExampleModule("example"))

    with pytest.raises(ModuleManagerError, match="already registered"):
        manager.register(ExampleModule("example"))


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        " ",
        "\t",
        " example",
        "example ",
    ],
)
def test_reject_invalid_module_identifiers(identifier):
    manager = ModuleManager()

    with pytest.raises(ModuleManagerError):
        manager.register(ExampleModule(identifier))


def test_reject_non_application_module():
    manager = ModuleManager()

    with pytest.raises(ModuleManagerError, match="ApplicationModule"):
        manager.register(object())


def test_resolve_dependency_order():
    manager = ModuleManager()

    pathway = ExampleModule(
        "pathways",
        dependencies=("entities",),
    )

    entities = ExampleModule("entities")

    manager.register(pathway)
    manager.register(entities)

    ordered = manager.resolve_order()

    assert [module.module_id for module in ordered] == [
        "entities",
        "pathways",
    ]


def test_resolve_multiple_dependencies():
    manager = ModuleManager()

    pathway = ExampleModule(
        "pathways",
        dependencies=("entities", "provenance"),
    )

    entities = ExampleModule("entities")
    provenance = ExampleModule("provenance")

    manager.register(pathway)
    manager.register(entities)
    manager.register(provenance)

    ordered_ids = [
        module.module_id
        for module in manager.resolve_order()
    ]

    assert ordered_ids.index("entities") < ordered_ids.index("pathways")
    assert ordered_ids.index("provenance") < ordered_ids.index("pathways")


def test_resolve_multilevel_dependencies():
    manager = ModuleManager()

    visualization = ExampleModule(
        "visualization",
        dependencies=("pathways",),
    )

    pathways = ExampleModule(
        "pathways",
        dependencies=("entities",),
    )

    entities = ExampleModule("entities")

    manager.register(visualization)
    manager.register(pathways)
    manager.register(entities)

    ordered_ids = [
        module.module_id
        for module in manager.resolve_order()
    ]

    assert ordered_ids == [
        "entities",
        "pathways",
        "visualization",
    ]


def test_preserve_deterministic_registration_order():
    manager = ModuleManager()

    manager.register(ExampleModule("first"))
    manager.register(ExampleModule("second"))
    manager.register(ExampleModule("third"))

    first_result = manager.resolve_order()
    second_result = manager.resolve_order()

    assert first_result == second_result

    assert [module.module_id for module in first_result] == [
        "first",
        "second",
        "third",
    ]


def test_missing_dependency():
    manager = ModuleManager()

    manager.register(
        ExampleModule(
            "pathways",
            dependencies=("entities",),
        )
    )

    with pytest.raises(ModuleManagerError, match="not registered"):
        manager.resolve_order()


def test_circular_dependency():
    manager = ModuleManager()

    manager.register(
        ExampleModule("module_a", dependencies=("module_b",))
    )

    manager.register(
        ExampleModule("module_b", dependencies=("module_a",))
    )

    with pytest.raises(ModuleManagerError, match="Circular"):
        manager.resolve_order()


def test_self_dependency():
    manager = ModuleManager()

    manager.register(
        ExampleModule(
            "module_a",
            dependencies=("module_a",),
        )
    )

    with pytest.raises(ModuleManagerError, match="Circular"):
        manager.resolve_order()


@pytest.mark.parametrize(
    "dependencies",
    [
        ["entities"],
        "entities",
        None,
    ],
)
def test_reject_invalid_dependency_declarations(dependencies):
    manager = ModuleManager()

    module = ExampleModule("pathways")
    module._dependencies = dependencies

    with pytest.raises(ModuleManagerError, match="tuple"):
        manager.register(module)


@pytest.mark.parametrize(
    "dependency_id",
    [
        "",
        " ",
        " entities",
        "entities ",
    ],
)
def test_reject_invalid_dependency_identifiers(dependency_id):
    manager = ModuleManager()

    module = ExampleModule(
        "pathways",
        dependencies=(dependency_id,),
    )

    with pytest.raises(ModuleManagerError):
        manager.register(module)


def test_registered_modules_are_returned_as_tuple():
    manager = ModuleManager()

    manager.register(ExampleModule("example"))

    assert isinstance(manager.modules, tuple)
    assert len(manager.modules) == 1


def test_registered_modules_preserve_registration_order():
    manager = ModuleManager()

    first = ExampleModule("first")
    second = ExampleModule("second")

    manager.register(first)
    manager.register(second)

    assert manager.modules == (first, second)
