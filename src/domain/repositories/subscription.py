
from abc import ABC, abstractmethod
from src.domain.models import User, Subscription


class AbstractSubscriptionRepository(ABC):
    """Port — defines what the application needs from a subscription store."""

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Subscription | None: ...

    @abstractmethod
    async def get_by_stripe_subscription_id(self, stripe_sub_id: str) -> Subscription | None: ...

    @abstractmethod
    async def create(self, user_id: int, status: str, **kwargs) -> Subscription: ...

    @abstractmethod
    async def update_status(self, subscription_id: int, status: str) -> None: ...

    @abstractmethod
    async def get_active_members(self) -> list[tuple[User, Subscription]]: ...
