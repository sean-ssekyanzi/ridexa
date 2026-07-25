
from abc import ABC, abstractmethod
from src.domain.models import User

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

