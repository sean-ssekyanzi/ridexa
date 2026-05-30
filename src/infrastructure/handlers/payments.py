from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request
from src.infrastructure.auth import get_current_token_payload
from src.infrastructure.di import get_service_container
from src.infrastructure.container import Container
from src.infrastructure.handlers.models import PayPalConfirm, MomoRequest
from src.infrastructure.payment import stripe as stripe_adapter, paypal, momo
from src.infrastructure.schemas.user import MemberOut
from src.application.services.user import UserService
from src.application.services.subscription import SubscriptionService

router = APIRouter(tags=["payments"])


@router.post("/create-checkout-session")
async def checkout(payload: dict = Depends(get_current_token_payload)):
    return {"url": stripe_adapter.create_checkout_session(payload["sub"])}


@router.post("/webhook")
@inject
async def webhook(
    request: Request,
    subscription_service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    container: Container = Depends(get_service_container)
):
    body = await request.body()
    event = stripe_adapter.parse_webhook(body, request.headers.get("stripe-signature"))

    if event["type"] == "checkout.session.completed":
        obj = event["data"]["object"]
        await subscription_service.activate_for_username(
            obj["metadata"]["username"],
            stripe_customer_id=obj.get("customer"),
            stripe_subscription_id=obj.get("subscription"),
        )
    elif event["type"] == "customer.subscription.deleted":
        await subscription_service.cancel(event["data"]["object"]["id"])

    return {"status": "ok"}


@router.post("/paypal-confirm")
@inject
async def paypal_confirm(
    body: PayPalConfirm,
    payload: dict = Depends(get_current_token_payload),
    user_service: UserService = Depends(Provide[Container.user_service]),
    subscription_service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    container: Container = Depends(get_service_container)
):
    await paypal.verify_order(body.order_id)
    user = await user_service.get_current_user(payload["sub"])
    await subscription_service.activate(user)
    return {"status": "ok"}


@router.post("/momo-pay")
@inject
async def momo_pay(
    body: MomoRequest,
    payload: dict = Depends(get_current_token_payload),
    user_service: UserService = Depends(Provide[Container.user_service]),
    subscription_service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    container: Container = Depends(get_service_container)
):
    reference = await momo.request_payment(body.phone)
    user = await user_service.get_current_user(payload["sub"])
    await subscription_service.activate(user)
    return {"status": "ok", "reference": reference}


@router.get("/members", response_model=list[MemberOut])
@inject
async def members(
    subscription_service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    container: Container = Depends(get_service_container)
):
    pairs = await subscription_service.list_members()
    return [MemberOut(username=u.username, status=s.status, started_at=s.started_at, expires_at=s.expires_at) for u, s in pairs]
