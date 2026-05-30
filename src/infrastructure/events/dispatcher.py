from src.domain.events.events import DomainEvent, AbstractDomainEventDispatcher


class InMemoryEventDispatcher(AbstractDomainEventDispatcher):
    """In-memory domain event dispatcher for local development and testing."""

    def __init__(self):
        self._handlers: dict = {}

    def subscribe(self, event_type: type, handler):
        """Register a handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: DomainEvent) -> None:
        """Dispatch event to all registered handlers."""
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            await handler(event) if callable(handler) else None
