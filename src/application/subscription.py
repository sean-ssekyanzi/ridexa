from datetime import datetime
from src.domain.models import User, Subscription
from src.domain.ports import UserRepository, SubscriptionRepository


async def activate_premium(user: User, user_repo: UserRepository, sub_repo: SubscriptionRepository, **kwargs) -> None:
    if user.is_premium:
        return
    await user_repo.set_premium(user.id, True)
    existing = await sub_repo.get_by_user_id(user.id)
    if existing:
        await sub_repo.update_status(existing.id, "active")
    else:
        await sub_repo.create(user_id=user.id, status="active", started_at=datetime.utcnow(), **kwargs)


async def cancel_premium(stripe_sub_id: str, user_repo: UserRepository, sub_repo: SubscriptionRepository) -> None:
    sub = await sub_repo.get_by_stripe_subscription_id(stripe_sub_id)
    if sub:
        await sub_repo.update_status(sub.id, "cancelled")
        await user_repo.set_premium(sub.user_id, False)


async def list_members(sub_repo: SubscriptionRepository) -> list[tuple[User, Subscription]]:
    return await sub_repo.get_active_members()
