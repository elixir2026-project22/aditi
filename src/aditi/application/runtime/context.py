
from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """
    Shared context supplied to application modules.

    The context provides application-level information
    without exposing another module's internal state.
    """

    application_name: str = "Aditi"

    config: Mapping[str, object] = field(
        default_factory=dict
    )
