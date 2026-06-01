"""
FastAPI handler layer for infrastructure.
This module contains handler classes wired to abstract service interfaces.
"""

from src.domain.use_cases import AbstractSubscriptionUseCases, AbstractUserService
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


class SubscriptionHandler:
    """Handler for subscription-related operations."""

    def __init__(self, sub_service: AbstractSubscriptionUseCases, event_dispatcher: AbstractDomainEventDispatcher | None = None):
        self._sub_service = sub_service
        self._event_dispatcher = event_dispatcher

    async def activate(self, user, **kwargs):
        return await self._sub_service.activate_premium(user, self._sub_service._user_repo, self._sub_service._sub_repo, **kwargs)

    async def cancel(self, stripe_sub_id: str):
        return await self._sub_service.cancel_premium(stripe_sub_id, self._sub_service._user_repo, self._sub_service._sub_repo)

    async def list_members(self):
        return await self._sub_service.list_members(self._sub_service._sub_repo)

    async def activate_for_username(self, username: str, **kwargs):
        return await self._sub_service.activate_for_username(username, **kwargs)
