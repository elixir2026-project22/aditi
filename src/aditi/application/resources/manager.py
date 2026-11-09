
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

ResourceDisposer = Callable[[Any], None]


@dataclass(slots=True)
class ResourceEntry:
    """Stores a resource and its optional cleanup operation."""

    resource: Any
    disposer: ResourceDisposer | None = None


class ResourceManagerError(RuntimeError):
    """Raised when resource management encounters an error."""


class ResourceCleanupError(RuntimeError):
    """Raised when one or more resources fail to release."""


class ResourceManager:
    """
    Central registry for application resources.

    Resources are identified by unique string keys.
    Optional disposer callbacks define how resources are released.
    """

    def __init__(self) -> None:
        self._resources: dict[str, ResourceEntry] = {}

    @property
    def resource_count(self) -> int:
        """Return the number of registered resources."""
        return len(self._resources)

    def register(
        self,
        key: str,
        resource: Any,
        disposer: ResourceDisposer | None = None,
    ) -> None:
        """Register a resource under a unique identifier."""

        if not isinstance(key, str) or not key.strip():
            raise ResourceManagerError(
                "Resource key must be a non-empty string."
            )

        if key in self._resources:
            raise ResourceManagerError(
                f"Resource '{key}' is already registered."
            )

        if disposer is not None and not callable(disposer):
            raise TypeError("Resource disposer must be callable.")

        self._resources[key] = ResourceEntry(
            resource=resource,
            disposer=disposer,
        )

    def get(
        self,
        key: str,
        expected_type: type | None = None,
    ) -> Any:
        """Retrieve a resource, optionally validating its type."""

        entry = self._resources.get(key)

        if entry is None:
            raise ResourceManagerError(
                f"Resource '{key}' is not registered."
            )

        resource = entry.resource

        if expected_type is not None and not isinstance(
            resource, expected_type
        ):
            raise TypeError(
                f"Resource '{key}' is not of type "
                f"'{expected_type.__name__}'."
            )

        return resource

    def contains(self, key: str) -> bool:
        """Check whether a resource is registered."""
        return key in self._resources

    def release(self, key: str) -> bool:
        """
        Release one resource.

        Returns False if the resource does not exist.
        The entry is removed before its disposer is invoked.
        """

        entry = self._resources.pop(key, None)

        if entry is None:
            return False

        if entry.disposer is not None:
            entry.disposer(entry.resource)

        return True

    def clear(self) -> None:
        """
        Release all resources in reverse registration order.

        Continue cleaning up remaining resources if a disposer fails.
        Aggregate cleanup errors after all resources have been processed.
        """

        entries = list(self._resources.values())
        self._resources.clear()

        errors = []

        for entry in reversed(entries):
            if entry.disposer is None:
                continue

            try:
                entry.disposer(entry.resource)
            except Exception as error: # noqa: BLE001
                errors.append(error)

        if errors:
            cleanup_errors = ExceptionGroup(
                "One or more resources failed to release.",
                errors,
            )

            raise ResourceCleanupError(
                f"{len(errors)} resource(s) failed to release."
            ) from cleanup_errors
