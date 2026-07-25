from abc import ABC, abstractmethod
from src.domain.models import User

class AbstractUserService(ABC):

    @abstractmethod
    async def register(self, username: str, password: str) -> User: ...

    @abstractmethod
    async def login(self, username: str, password: str) -> str: ...

    @abstractmethod
    async def get_current_user(self, username: str) -> User: ...

    @abstractmethod
    async def list_users(self) -> list[User]: ...


