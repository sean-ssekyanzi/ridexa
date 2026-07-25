from abc import ABC, abstractmethod
from src.domain.events.events import PremiumActivatedEvent, PremiumCancelledEvent
from src.domain.models import User, Subscription
from src.domain.repositories import AbstractUserRepository, AbstractSubscriptionRepository


class AbstractSubscriptionUseCases(ABC):

    @abstractmethod
    async def activate_premium(self, user: User, user_repo: AbstractUserRepository,
                               sub_repo: AbstractSubscriptionRepository, **kwargs) -> PremiumActivatedEvent | None: ...

    @abstractmethod
    async def cancel_premium(self, stripe_sub_id: str, user_repo: AbstractUserRepository,
                             sub_repo: AbstractSubscriptionRepository) -> PremiumCancelledEvent | None: ...

    @abstractmethod
    async def list_members(self, sub_repo: AbstractSubscriptionRepository) -> list[tuple[User, Subscription]]: ...

