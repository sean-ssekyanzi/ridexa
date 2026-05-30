from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from src.infrastructure.di import get_service_container
from src.infrastructure.container import Container
from src.application.services.subscription import SubscriptionService

router = APIRouter(prefix="/admin", tags=["subscriptions"])


@router.post("/activate-premium/{username}")
@inject
async def admin_activate(
    username: str,
    subscription_service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    container: Container = Depends(get_service_container)
):
    await subscription_service.activate_for_username(username)
    return {"status": "ok", "username": username, "is_premium": True}
