
from dataclasses import dataclass

import pytest

from aditi.application.events.base import ApplicationEvent
from aditi.application.events.dispatcher import EventDispatcher


@dataclass(frozen=True, slots=True)
class PathwayLoaded(ApplicationEvent):
    pathway_id: str


@dataclass(frozen=True, slots=True)
class EntityRegistered(ApplicationEvent):
    entity_id: str


def test_event_metadata():
    event = PathwayLoaded("pathway_001")

    assert event.event_id is not None
    assert event.occurred_at.tzinfo is not None
    assert event.correlation_id is None


def test_subscribe_and_publish():
    dispatcher = EventDispatcher()
    received = []

    dispatcher.subscribe(
        PathwayLoaded,
        lambda event: received.append(event.pathway_id),
    )

    count = dispatcher.publish(PathwayLoaded("pathway_001"))

    assert count == 1
    assert received == ["pathway_001"]


def test_multiple_subscribers():
    dispatcher = EventDispatcher()
    received = []

    dispatcher.subscribe(
        PathwayLoaded,
        lambda event: received.append("first"),
    )

    dispatcher.subscribe(
        PathwayLoaded,
        lambda event: received.append("second"),
    )

    count = dispatcher.publish(PathwayLoaded("pathway_001"))

    assert count == 2
    assert received == ["first", "second"]


def test_unsubscribe():
    dispatcher = EventDispatcher()
    received = []

    subscription = dispatcher.subscribe(
        PathwayLoaded,
        lambda event: received.append(event.pathway_id),
    )

    assert dispatcher.unsubscribe(subscription) is True

    count = dispatcher.publish(PathwayLoaded("pathway_001"))

    assert count == 0
    assert received == []


def test_unsubscribe_unknown_subscription():
    dispatcher = EventDispatcher()

    subscription = dispatcher.subscribe(
        PathwayLoaded,
        lambda event: None,
    )

    dispatcher.unsubscribe(subscription)

    assert dispatcher.unsubscribe(subscription) is False


def test_duplicate_subscriptions_are_independent():
    dispatcher = EventDispatcher()
    received = []

    handler = lambda event: received.append("received")

    first = dispatcher.subscribe(PathwayLoaded, handler)
    second = dispatcher.subscribe(PathwayLoaded, handler)

    dispatcher.unsubscribe(first)

    dispatcher.publish(PathwayLoaded("pathway_001"))

    assert received == ["received"]
    assert first.subscription_id != second.subscription_id


def test_event_types_are_dispatched_independently():
    dispatcher = EventDispatcher()
    received = []

    dispatcher.subscribe(
        PathwayLoaded,
        lambda event: received.append("pathway"),
    )

    dispatcher.subscribe(
        EntityRegistered,
        lambda event: received.append("entity"),
    )

    dispatcher.publish(EntityRegistered("entity_001"))

    assert received == ["entity"]


def test_unsubscription_during_dispatch_uses_snapshot():
    dispatcher = EventDispatcher()
    received = []

    second_subscription = None

    def first_handler(event):
        received.append("first")
        dispatcher.unsubscribe(second_subscription)

    dispatcher.subscribe(PathwayLoaded, first_handler)

    second_subscription = dispatcher.subscribe(
        PathwayLoaded,
        lambda event: received.append("second"),
    )

    dispatcher.publish(PathwayLoaded("pathway_001"))

    assert received == ["first", "second"]

    received.clear()

    dispatcher.publish(PathwayLoaded("pathway_002"))

    assert received == ["first"]


def test_handler_exception_propagates():
    dispatcher = EventDispatcher()

    def failing_handler(event):
        raise RuntimeError("Subscriber failed.")

    dispatcher.subscribe(PathwayLoaded, failing_handler)

    with pytest.raises(RuntimeError, match="Subscriber failed"):
        dispatcher.publish(PathwayLoaded("pathway_001"))


def test_reject_invalid_event_type():
    dispatcher = EventDispatcher()

    with pytest.raises(TypeError):
        dispatcher.subscribe(str, lambda event: None)


def test_reject_invalid_published_object():
    dispatcher = EventDispatcher()

    with pytest.raises(TypeError):
        dispatcher.publish("not an event")
