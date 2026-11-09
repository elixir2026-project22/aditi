
from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID, uuid4

from aditi.application.events.base import ApplicationEvent


@dataclass(frozen=True, slots=True)
class Subscription:
    """Identifies an event subscription."""

    event_type: type[ApplicationEvent]
    subscription_id: UUID


class EventDispatcher:
    """
    Distributes application events to registered subscribers.

    Event delivery is synchronous. Subscribers receive events
    in registration order.
    """

    def __init__(self) -> None:
        self._handlers: dict[
            type[ApplicationEvent],
            dict[UUID, Callable[[ApplicationEvent], None]],
        ] = {}

    def subscribe(
        self,
        event_type: type[ApplicationEvent],
        handler: Callable[[ApplicationEvent], None],
    ) -> Subscription:
        """Register a handler for a specific event type."""

        if not isinstance(event_type, type) or not issubclass(
            event_type, ApplicationEvent
        ):
            raise TypeError(
                "Event type must inherit from ApplicationEvent."
            )

        if not callable(handler):
            raise TypeError("Event handler must be callable.")

        subscription_id = uuid4()

        self._handlers.setdefault(event_type, {})[
            subscription_id
        ] = handler

        return Subscription(
            event_type=event_type,
            subscription_id=subscription_id,
        )

    def unsubscribe(self, subscription: Subscription) -> bool:
        """
        Remove a subscription.

        Returns True if the subscription existed, otherwise False.
        """

        handlers = self._handlers.get(subscription.event_type)

        if handlers is None:
            return False

        if subscription.subscription_id not in handlers:
            return False

        del handlers[subscription.subscription_id]

        if not handlers:
            del self._handlers[subscription.event_type]

        return True

    def publish(self, event: ApplicationEvent) -> int:
        """
        Deliver an event to its registered handlers.

        A snapshot is used so subscriptions can change safely
        while an event is being dispatched.

        Handler exceptions propagate to the publisher.
        """

        if not isinstance(event, ApplicationEvent):
            raise TypeError(
                "Published events must inherit from ApplicationEvent."
            )

        handlers = self._handlers.get(type(event), {})

        subscribers = tuple(handlers.values())

        for handler in subscribers:
            handler(event)

        return len(subscribers)
