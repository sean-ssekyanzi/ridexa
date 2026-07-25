from datetime import datetime
from src.domain.events.events import PremiumActivatedEvent, PremiumCancelledEvent, AbstractDomainEventDispatcher
from src.domain.models import User, Subscription
from src.domain.repositories import AbstractUserRepository, AbstractSubscriptionRepository
from src.domain.use_cases import AbstractSubscriptionUseCases
from src.domain.models.exceptions import SubscriptionNotFoundError


class SubscriptionService(AbstractSubscriptionUseCases):

    def __init__(self, user_repo: AbstractUserRepository, sub_repo: AbstractSubscriptionRepository, 
                 event_dispatcher: AbstractDomainEventDispatcher | None = None):
        self._user_repo = user_repo
        self._sub_repo = sub_repo
        self._event_dispatcher = event_dispatcher

    # Domain use-case implementations
    async def activate_premium(self, user: User, user_repo: AbstractUserRepository,
                               sub_repo: AbstractSubscriptionRepository, **kwargs) -> PremiumActivatedEvent | None:
        if user.is_premium:
            return None

        await user_repo.set_premium(user.id, True)
        existing = await sub_repo.get_by_user_id(user.id)
        if existing:
            await sub_repo.update_status(existing.id, "active")
            event = PremiumActivatedEvent(
                user_id=user.id,
                subscription_id=existing.id,
                status="active",
                started_at=existing.started_at,
                stripe_customer_id=kwargs.get("stripe_customer_id"),
                stripe_subscription_id=kwargs.get("stripe_subscription_id"),
                expires_at=kwargs.get("expires_at"),
            )
            if self._event_dispatcher:
                await self._event_dispatcher.dispatch(event)
            return event

        sub = await sub_repo.create(user_id=user.id, status="active", started_at=datetime.utcnow(), **kwargs)
        event = PremiumActivatedEvent(
            user_id=user.id,
            subscription_id=sub.id,
            status="active",
            started_at=sub.started_at,
            stripe_customer_id=kwargs.get("stripe_customer_id"),
            stripe_subscription_id=kwargs.get("stripe_subscription_id"),
            expires_at=kwargs.get("expires_at"),
        )
        if self._event_dispatcher:
            await self._event_dispatcher.dispatch(event)
        return event

    async def cancel_premium(self, stripe_sub_id: str, user_repo: AbstractUserRepository,
                             sub_repo: AbstractSubscriptionRepository) -> PremiumCancelledEvent | None:
        sub = await sub_repo.get_by_stripe_subscription_id(stripe_sub_id)
        if not sub:
            raise SubscriptionNotFoundError(f"Subscription '{stripe_sub_id}' not found")

        await sub_repo.update_status(sub.id, "cancelled")
        await user_repo.set_premium(sub.user_id, False)
        event = PremiumCancelledEvent(
            user_id=sub.user_id,
            subscription_id=sub.id,
            stripe_subscription_id=sub.stripe_subscription_id,
        )
        if self._event_dispatcher:
            await self._event_dispatcher.dispatch(event)
        return event

    async def list_members(self, sub_repo: AbstractSubscriptionRepository) -> list[tuple[User, Subscription]]:
        return await sub_repo.get_active_members()

    # Helper method for activating by username
    async def activate_for_username(self, username: str, **kwargs) -> PremiumActivatedEvent | None:
        user = await self._user_repo.get_by_username(username)
        if user:
            return await self.activate_premium(user, self._user_repo, self._sub_repo, **kwargs)
        return None
