
from abc import ABC, abstractmethod
from datetime import timedelta

class AbstractAuthRepository(ABC):
    """Port — defines what the application needs from an auth/token store."""

    @abstractmethod
    async def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str: ...

    @abstractmethod
    async def verify_token(self, token: str) -> dict: ...

