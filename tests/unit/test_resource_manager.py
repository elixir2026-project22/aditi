
import pytest

from aditi.application.resources.manager import (
    ResourceCleanupError,
    ResourceManager,
    ResourceManagerError,
)


def test_register_resource():
    manager = ResourceManager()
    resource = {"name": "pathway_data"}

    manager.register("pathway", resource)

    assert manager.get("pathway") is resource
    assert manager.resource_count == 1


def test_prevent_duplicate_resource_registration():
    manager = ResourceManager()

    manager.register("pathway", {"name": "first"})

    with pytest.raises(ResourceManagerError):
        manager.register("pathway", {"name": "second"})


def test_retrieve_missing_resource():
    manager = ResourceManager()

    with pytest.raises(ResourceManagerError, match="not registered"):
        manager.get("missing")


def test_validate_resource_type():
    manager = ResourceManager()

    manager.register("dataset", [1, 2, 3])

    assert manager.get("dataset", list) == [1, 2, 3]


def test_reject_incorrect_resource_type():
    manager = ResourceManager()

    manager.register("dataset", [1, 2, 3])

    with pytest.raises(TypeError):
        manager.get("dataset", dict)


def test_check_resource_existence():
    manager = ResourceManager()

    manager.register("dataset", [1, 2, 3])

    assert manager.contains("dataset") is True
    assert manager.contains("missing") is False


def test_release_resource():
    manager = ResourceManager()
    released = []

    manager.register(
        "dataset",
        [1, 2, 3],
        disposer=lambda resource: released.append(resource),
    )

    assert manager.release("dataset") is True
    assert manager.contains("dataset") is False
    assert manager.resource_count == 0
    assert released == [[1, 2, 3]]


def test_release_missing_resource():
    manager = ResourceManager()

    assert manager.release("missing") is False


def test_clear_releases_resources_in_reverse_order():
    manager = ResourceManager()
    released = []

    manager.register(
        "first",
        "resource_a",
        disposer=lambda resource: released.append(resource),
    )

    manager.register(
        "second",
        "resource_b",
        disposer=lambda resource: released.append(resource),
    )

    manager.register(
        "third",
        "resource_c",
        disposer=lambda resource: released.append(resource),
    )

    manager.clear()

    assert released == [
        "resource_c",
        "resource_b",
        "resource_a",
    ]

    assert manager.resource_count == 0


def test_clear_continues_after_disposer_failure():
    manager = ResourceManager()
    released = []

    def failing_disposer(resource):
        released.append(resource)
        raise RuntimeError("Cleanup failed.")

    manager.register(
        "first",
        "resource_a",
        disposer=lambda resource: released.append(resource),
    )

    manager.register(
        "second",
        "resource_b",
        disposer=failing_disposer,
    )

    manager.register(
        "third",
        "resource_c",
        disposer=lambda resource: released.append(resource),
    )

    with pytest.raises(ResourceCleanupError) as error_info:
        manager.clear()

    assert released == [
        "resource_c",
        "resource_b",
        "resource_a",
    ]

    assert isinstance(error_info.value.__cause__, ExceptionGroup)
    assert manager.resource_count == 0


def test_resource_without_disposer_can_be_released():
    manager = ResourceManager()

    manager.register("dataset", {"values": [1, 2, 3]})

    assert manager.release("dataset") is True
    assert manager.resource_count == 0


def test_reject_invalid_resource_key():
    manager = ResourceManager()

    with pytest.raises(ResourceManagerError):
        manager.register("", object())


def test_reject_invalid_disposer():
    manager = ResourceManager()

    with pytest.raises(TypeError):
        manager.register(
            "dataset",
            object(),
            disposer="not_callable",
        )
