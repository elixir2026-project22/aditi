
from aditi.application.modules.base import ApplicationModule


class ModuleManagerError(RuntimeError):
    """Raised when module management encounters an error."""


class ModuleManager:
    """
    Registers application modules and resolves their dependencies.

    The manager determines a valid initialization order while
    keeping individual module implementations independent.
    """

    def __init__(self) -> None:
        self._modules: dict[str, ApplicationModule] = {}

    @property
    def modules(self) -> tuple[ApplicationModule, ...]:
        """Return registered modules without exposing the registry."""
        return tuple(self._modules.values())

    @staticmethod
    def _validate_identifier(identifier: object, label: str) -> str:
        """Validate a module or dependency identifier."""

        if not isinstance(identifier, str) or not identifier.strip():
            raise ModuleManagerError(
                f"{label} must be a non-empty string."
            )

        if identifier != identifier.strip():
            raise ModuleManagerError(
                f"{label} cannot contain leading or trailing whitespace."
            )

        return identifier

    @classmethod
    def _validate_dependencies(
        cls,
        dependencies: object,
    ) -> tuple[str, ...]:
        """Validate a module's dependency declaration."""

        if not isinstance(dependencies, tuple):
            raise ModuleManagerError(
                "Module dependencies must be declared as a tuple."
            )

        validated: list[str] = []

        for dependency_id in dependencies:
            validated.append(
                cls._validate_identifier(
                    dependency_id,
                    "Dependency identifier",
                )
            )

        return tuple(validated)

    def register(self, module: ApplicationModule) -> None:
        """Register an application module."""

        if not isinstance(module, ApplicationModule):
            raise ModuleManagerError(
                "Registered modules must implement ApplicationModule."
            )

        module_id = self._validate_identifier(
            module.module_id,
            "Module identifier",
        )

        self._validate_dependencies(module.dependencies)

        if module_id in self._modules:
            raise ModuleManagerError(
                f"Module '{module_id}' is already registered."
            )

        self._modules[module_id] = module

    def get(self, module_id: str) -> ApplicationModule | None:
        """Retrieve a registered module by identifier."""
        return self._modules.get(module_id)

    def resolve_order(self) -> tuple[ApplicationModule, ...]:
        """
        Resolve dependencies using depth-first traversal.

        Dependencies are placed before the modules that require them.
        Registration order and dependency declaration order are preserved.
        """

        resolved: list[ApplicationModule] = []
        visited: set[str] = set()
        visiting: set[str] = set()

        def visit(module_id: str) -> None:

            if module_id in visited:
                return

            if module_id in visiting:
                raise ModuleManagerError(
                    f"Circular module dependency detected at '{module_id}'."
                )

            module = self._modules.get(module_id)

            if module is None:
                raise ModuleManagerError(
                    f"Required module '{module_id}' is not registered."
                )

            visiting.add(module_id)

            dependencies = self._validate_dependencies(
                module.dependencies
            )

            for dependency_id in dependencies:
                visit(dependency_id)

            visiting.remove(module_id)
            visited.add(module_id)
            resolved.append(module)

        for module_id in self._modules:
            visit(module_id)

        return tuple(resolved)
