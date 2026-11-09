
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class ExternalIdentifier:
    """
    Represents an identifier assigned by an external
    biological database or identifier system.
    """

    namespace: str
    value: str
    url: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.namespace, str) or not self.namespace.strip():
            raise ValueError(
                "External identifier namespace must be a non-empty string."
            )

        if self.namespace != self.namespace.strip():
            raise ValueError(
                "External identifier namespace cannot contain "
                "leading or trailing whitespace."
            )

        if not isinstance(self.value, str) or not self.value.strip():
            raise ValueError(
                "External identifier value must be a non-empty string."
            )

        if self.value != self.value.strip():
            raise ValueError(
                "External identifier value cannot contain "
                "leading or trailing whitespace."
            )

        if self.url is not None:
            self._validate_url(self.url)

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate an optional HTTP or HTTPS reference URL."""

        if not isinstance(url, str) or not url.strip():
            raise ValueError(
                "External identifier URL must be a non-empty string."
            )

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(
                "External identifier URL must be a valid HTTP or HTTPS URL."
            )

    @property
    def qualified_value(self) -> str:
        """Return the namespace-qualified identifier."""
        return f"{self.namespace}:{self.value}"
