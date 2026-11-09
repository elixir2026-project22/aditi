from threading import Thread

import pytest

from aditi.application.runtime.cancellation import (
    CancellationTokenSource,
    OperationCancelledError,
)


def test_token_is_not_cancelled_initially():
    source = CancellationTokenSource()

    assert source.token.is_cancelled is False


def test_cancel_requests_cancellation():
    source = CancellationTokenSource()

    assert source.cancel() is True
    assert source.token.is_cancelled is True


def test_cancel_is_idempotent():
    source = CancellationTokenSource()

    assert source.cancel() is True
    assert source.cancel() is False


def test_token_detects_cancellation():
    source = CancellationTokenSource()

    source.cancel()

    with pytest.raises(OperationCancelledError):
        source.token.throw_if_cancelled()


def test_token_does_not_raise_before_cancellation():
    source = CancellationTokenSource()

    source.token.throw_if_cancelled()


def test_token_wait_returns_false_on_timeout():
    source = CancellationTokenSource()

    assert source.token.wait(timeout=0.01) is False


def test_token_wait_detects_cancellation():
    source = CancellationTokenSource()

    source.cancel()

    assert source.token.wait(timeout=0) is True


def test_cancellation_is_shared_between_threads():
    source = CancellationTokenSource()
    results: list[bool] = []

    def request_cancellation() -> None:
        results.append(source.cancel())

    threads = [
        Thread(target=request_cancellation)
        for _ in range(10)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert results.count(True) == 1
    assert results.count(False) == 9
    assert source.token.is_cancelled