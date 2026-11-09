
from aditi.visualization.pathways.layouts.base import (
    PathwayLayoutAlgorithm,
)


class LayoutRegistryError(RuntimeError):
    """Raised when layout registration or lookup fails."""


class PathwayLayoutRegistry:
    """
    Stores and resolves pathway layout algorithms.

    Algorithms are registered under stable identifiers so that
    application services and API endpoints do not need to know
    their concrete implementation classes.
    """

    def __init__(self) -> None:
        self._algorithms: dict[str, PathwayLayoutAlgorithm] = {}

    @staticmethod
    def _validate_identifier(identifier: object) -> str:
        """Validate a layout identifier."""

        if not isinstance(identifier, str) or not identifier.strip():
            raise LayoutRegistryError(
                "Layout identifier must be a non-empty string."
            )

        if identifier != identifier.strip():
            raise LayoutRegistryError(
                "Layout identifier cannot contain leading "
                "or trailing whitespace."
            )

        return identifier

    def register(
        self,
        identifier: str,
        algorithm: PathwayLayoutAlgorithm,
    ) -> None:
        """Register a layout algorithm."""

        identifier = self._validate_identifier(identifier)

        if not isinstance(algorithm, PathwayLayoutAlgorithm):
            raise LayoutRegistryError(
                "Registered algorithms must implement "
                "PathwayLayoutAlgorithm."
            )

        if identifier in self._algorithms:
            raise LayoutRegistryError(
                f"Layout '{identifier}' is already registered."
            )

        self._algorithms[identifier] = algorithm

    def get(
        self,
        identifier: str,
    ) -> PathwayLayoutAlgorithm | None:
        """Retrieve a registered algorithm, if available."""

        identifier = self._validate_identifier(identifier)

        return self._algorithms.get(identifier)

    def resolve(
        self,
        identifier: str,
    ) -> PathwayLayoutAlgorithm:
        """Retrieve an algorithm or raise an informative error."""

        identifier = self._validate_identifier(identifier)

        algorithm = self._algorithms.get(identifier)

        if algorithm is None:
            raise LayoutRegistryError(
                f"Layout '{identifier}' is not registered."
            )

        return algorithm

    @property
    def available_layouts(self) -> tuple[str, ...]:
        """Return registered layout identifiers in registration order."""

        return tuple(self._algorithms)
