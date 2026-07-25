from typing import Optional, List, Tuple

from src.domain.use_cases.subscription import AbstractSubscriptionUseCases
from src.domain.use_cases.user import AbstractUserService
from src.domain.events.events import (
    AbstractDomainEventDispatcher,
    PremiumActivatedEvent,
    PremiumCancelledEvent,
)
from src.domain.models import User, Subscription


class SubscriptionHandler:
    """Handler for subscription-related operations.

    This class is a thin wrapper around application services and exposes
    convenience methods used by infrastructure layers (HTTP handlers, jobs).
    It will try to use the repositories attached to the provided services.
    """

    def __init__(
        self,
        user_service: AbstractUserService,
        sub_service: AbstractSubscriptionUseCases,
        event_dispatcher: Optional[AbstractDomainEventDispatcher] = None,
    ) -> None:
        self._user_service = user_service
        self._sub_service = sub_service
        self._event_dispatcher = event_dispatcher

    async def activate(self, user: User, **kwargs) -> Optional[PremiumActivatedEvent]:
        """Activate premium for a given `User`.

        Delegates to the subscription service and passes the user & repositories.
        """
        user_repo = getattr(self._user_service, "_repo", None)
        sub_repo = getattr(self._sub_service, "_sub_repo", None)
        return await self._sub_service.activate_premium(user, user_repo, sub_repo, **kwargs)


    async def cancel(self, stripe_sub_id: str) -> Optional[PremiumCancelledEvent]:
        """Cancel a subscription by Stripe subscription id."""
        user_repo = getattr(self._user_service, "_repo", None)
        sub_repo = getattr(self._sub_service, "_sub_repo", None)
        return await self._sub_service.cancel_premium(stripe_sub_id, user_repo, sub_repo)

    async def list_members(self) -> List[Tuple[User, Subscription]]:
        """Return active premium members as (User, Subscription) pairs."""
        sub_repo = getattr(self._sub_service, "_sub_repo", None)
        return await self._sub_service.list_members(sub_repo)
