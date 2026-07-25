"""
FastAPI handler layer for infrastructure.
This module contains handler classes wired to abstract service interfaces.
"""
from src.domain.use_cases.user import AbstractUserService
from src.domain.events.events import AbstractDomainEventDispatcher


class UserHandler:
    """Handler for user-related operations."""

    def __init__(self, user_service: AbstractUserService, event_dispatcher: AbstractDomainEventDispatcher | None = None):
        self._user_service = user_service
        self._event_dispatcher = event_dispatcher

    async def register(self, username: str, password: str):
        return await self._user_service.register(username, password)

    async def login(self, username: str, password: str):
        return await self._user_service.login(username, password)

    async def get_current_user(self, username: str):
        return await self._user_service.get_current_user(username)

    async def list_users(self):
        return await self._user_service.list_users()


