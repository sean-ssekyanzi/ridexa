
from abc import ABC, abstractmethod
from src.domain.models import User, Subscription
from datetime import timedelta
class AbstractAuthRepository(ABC):
    """Port — defines what the application needs from an auth/token store."""

    @abstractmethod
    async def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str: ...

    @abstractmethod
    async def verify_token(self, token: str) -> dict: ...


class AbstractUserRepository(ABC):
    """Port — defines what the application needs from a user store."""

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def create(self, username: str, hashed_password: str) -> User: ...

    @abstractmethod
    async def get_all(self) -> list[User]: ...

    @abstractmethod
    async def set_premium(self, user_id: int, is_premium: bool) -> None: ...


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
