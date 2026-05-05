from datetime import datetime
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api.deps import get_user_repo, get_sub_repo, get_current_token_payload
from src.application.user import get_current_user
from src.application.subscription import activate_premium, cancel_premium, list_members
from src.infrastructure.db.repositories import SQLUserRepository, SQLSubscriptionRepository
from src.infrastructure.payment import stripe as stripe_adapter, paypal, momo
from src.db.schemas import MemberOut

router = APIRouter()


@router.post("/create-checkout-session")
async def checkout(payload: dict = Depends(get_current_token_payload)):
    url = stripe_adapter.create_checkout_session(payload["sub"])
    return {"url": url}


@router.post("/webhook")
async def webhook(request: Request, user_repo: SQLUserRepository = Depends(get_user_repo),
                  sub_repo: SQLSubscriptionRepository = Depends(get_sub_repo)):
    body = await request.body()
    event = stripe_adapter.parse_webhook(body, request.headers.get("stripe-signature"))

    if event["type"] == "checkout.session.completed":
        obj = event["data"]["object"]
        user = await user_repo.get_by_username(obj["metadata"]["username"])
        if user:
            await activate_premium(user, user_repo, sub_repo,
                                   stripe_customer_id=obj.get("customer"),
                                   stripe_subscription_id=obj.get("subscription"))

    elif event["type"] == "customer.subscription.deleted":
        await cancel_premium(event["data"]["object"]["id"], user_repo, sub_repo)

    return {"status": "ok"}


class PayPalConfirm(BaseModel):
    order_id: str


@router.post("/paypal-confirm")
async def paypal_confirm(body: PayPalConfirm, payload: dict = Depends(get_current_token_payload),
                         user_repo: SQLUserRepository = Depends(get_user_repo),
                         sub_repo: SQLSubscriptionRepository = Depends(get_sub_repo)):
    await paypal.verify_order(body.order_id)
    user = await get_current_user(payload["sub"], user_repo)
    await activate_premium(user, user_repo, sub_repo)
    return {"status": "ok"}


class MomoRequest(BaseModel):
    phone: str


@router.post("/momo-pay")
async def momo_pay(body: MomoRequest, payload: dict = Depends(get_current_token_payload),
                   user_repo: SQLUserRepository = Depends(get_user_repo),
                   sub_repo: SQLSubscriptionRepository = Depends(get_sub_repo)):
    reference = await momo.request_payment(body.phone)
    user = await get_current_user(payload["sub"], user_repo)
    await activate_premium(user, user_repo, sub_repo)
    return {"status": "ok", "reference": reference}


@router.get("/members", response_model=list[MemberOut])
async def members(sub_repo: SQLSubscriptionRepository = Depends(get_sub_repo)):
    pairs = await list_members(sub_repo)
    return [MemberOut(username=u.username, status=s.status,
                      started_at=s.started_at, expires_at=s.expires_at) for u, s in pairs]
