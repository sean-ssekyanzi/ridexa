from abc import ABC, abstractmethod

# Re-export repository abstractions for convenience
from .repositories import AbstractUserRepository, AbstractSubscriptionRepository
from .events.events import AbstractDomainEventDispatcher

# Aliases used by existing infrastructure code
UserRepository = AbstractUserRepository
SubscriptionRepository = AbstractSubscriptionRepository
EventDispatcher = AbstractDomainEventDispatcher


class AbstractPaymentService(ABC):
    """Port — external payment provider."""

    @abstractmethod
    async def verify(self, reference: str) -> bool: ...


# Backwards compat alias
PaymentPort = AbstractPaymentService
