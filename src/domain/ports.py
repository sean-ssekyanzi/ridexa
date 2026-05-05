from abc import ABC, abstractmethod
from src.domain.models import User, Subscription


class UserRepository(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def create(self, username: str, hashed_password: str) -> User: ...

    @abstractmethod
    async def get_all(self) -> list[User]: ...

    @abstractmethod
    async def set_premium(self, user_id: int, is_premium: bool) -> None: ...


class SubscriptionRepository(ABC):
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


class PaymentPort(ABC):
    @abstractmethod
    async def verify(self, reference: str) -> bool: ...
