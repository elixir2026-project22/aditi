from threading import Event, Lock


class OperationCancelledError(Exception):
    """Raised when an operation observes a cancellation request."""


class CancellationToken:
    """
    Read-only cancellation interface provided to an operation.

    The token does not expose the ability to request cancellation.
    """

    def __init__(self, event: Event) -> None:
        self._event = event

    @property
    def is_cancelled(self) -> bool:
        """Return whether cancellation has been requested."""
        return self._event.is_set()

    def throw_if_cancelled(self) -> None:
        """Raise an exception if cancellation has been requested."""

        if self.is_cancelled:
            raise OperationCancelledError(
                "The operation was cancelled."
            )

    def wait(self, timeout: float | None = None) -> bool:
        """
        Wait until cancellation is requested or the timeout expires.

        Returns True if cancellation was requested, otherwise False.
        """
        return self._event.wait(timeout)


class CancellationTokenSource:
    """
    Owns a cancellation signal and provides its associated token.

    Call cancel() to request cancellation of an operation.
    """

    def __init__(self) -> None:
        self._event = Event()
        self._token = CancellationToken(self._event)
        self._lock = Lock()

    @property
    def token(self) -> CancellationToken:
        """Return the cancellation token associated with this source."""
        return self._token

    @property
    def is_cancelled(self) -> bool:
        """Return whether cancellation has been requested."""
        return self._event.is_set()

    def cancel(self) -> bool:
        """
        Request cancellation.

        Returns True when cancellation is requested for the first time.
        Returns False if cancellation was already requested.
        """
        with self._lock:
            if self._event.is_set():
                return False

            self._event.set()
            return True