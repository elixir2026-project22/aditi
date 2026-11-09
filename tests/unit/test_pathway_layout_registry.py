
import pytest

from aditi.visualization.pathways.layouts import (
    ForceDirectedLayout,
    HierarchicalLayout,
    LayoutRegistryError,
    PathwayLayoutRegistry,
)


def create_registry() -> PathwayLayoutRegistry:
    registry = PathwayLayoutRegistry()

    registry.register(
        "hierarchical",
        HierarchicalLayout(),
    )

    registry.register(
        "force-directed",
        ForceDirectedLayout(),
    )

    return registry


def test_registry_starts_empty() -> None:
    registry = PathwayLayoutRegistry()

    assert registry.available_layouts == ()


def test_registry_registers_algorithm() -> None:
    registry = PathwayLayoutRegistry()
    algorithm = HierarchicalLayout()

    registry.register("hierarchical", algorithm)

    assert registry.get("hierarchical") is algorithm


def test_registry_registers_multiple_algorithms() -> None:
    registry = create_registry()

    assert registry.available_layouts == (
        "hierarchical",
        "force-directed",
    )


def test_registry_preserves_registration_order() -> None:
    registry = create_registry()

    assert registry.available_layouts[0] == "hierarchical"
    assert registry.available_layouts[1] == "force-directed"


def test_registry_resolves_hierarchical_layout() -> None:
    registry = create_registry()

    algorithm = registry.resolve("hierarchical")

    assert isinstance(algorithm, HierarchicalLayout)


def test_registry_resolves_force_directed_layout() -> None:
    registry = create_registry()

    algorithm = registry.resolve("force-directed")

    assert isinstance(algorithm, ForceDirectedLayout)


def test_registry_returns_none_for_unknown_layout() -> None:
    registry = PathwayLayoutRegistry()

    assert registry.get("unknown") is None


def test_registry_raises_for_unknown_layout() -> None:
    registry = PathwayLayoutRegistry()

    with pytest.raises(LayoutRegistryError):
        registry.resolve("unknown")


def test_registry_rejects_duplicate_identifier() -> None:
    registry = PathwayLayoutRegistry()

    registry.register(
        "hierarchical",
        HierarchicalLayout(),
    )

    with pytest.raises(LayoutRegistryError):
        registry.register(
            "hierarchical",
            ForceDirectedLayout(),
        )


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        " ",
        "\t",
        "\n",
        None,
        123,
    ],
)
def test_registry_rejects_invalid_identifiers(
    identifier: object,
) -> None:
    registry = PathwayLayoutRegistry()

    with pytest.raises(LayoutRegistryError):
        registry.register(
            identifier,
            HierarchicalLayout(),
        )


@pytest.mark.parametrize(
    "identifier",
    [
        " hierarchical",
        "hierarchical ",
        " hierarchical ",
    ],
)
def test_registry_rejects_identifiers_with_outer_whitespace(
    identifier: str,
) -> None:
    registry = PathwayLayoutRegistry()

    with pytest.raises(LayoutRegistryError):
        registry.register(
            identifier,
            HierarchicalLayout(),
        )


def test_registry_rejects_invalid_algorithm() -> None:
    registry = PathwayLayoutRegistry()

    with pytest.raises(LayoutRegistryError):
        registry.register(
            "invalid",
            "not a layout algorithm",
        )


def test_registry_does_not_replace_existing_algorithm() -> None:
    registry = PathwayLayoutRegistry()
    original = HierarchicalLayout()

    registry.register("hierarchical", original)

    with pytest.raises(LayoutRegistryError):
        registry.register(
            "hierarchical",
            ForceDirectedLayout(),
        )

    assert registry.resolve("hierarchical") is original


def test_registry_get_rejects_invalid_identifier() -> None:
    registry = PathwayLayoutRegistry()

    with pytest.raises(LayoutRegistryError):
        registry.get(" ")


def test_registry_resolve_rejects_invalid_identifier() -> None:
    registry = PathwayLayoutRegistry()

    with pytest.raises(LayoutRegistryError):
        registry.resolve("")
