import os
import stripe
from fastapi import HTTPException, Request
from src.domain.ports import PaymentPort

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def create_checkout_session(username: str) -> str:
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": os.getenv("STRIPE_PRICE_ID"), "quantity": 1}],
        success_url=f"{FRONTEND_URL}/protected?premium=success",
        cancel_url=f"{FRONTEND_URL}/premium",
        metadata={"username": username},
    )
    return session.url


def parse_webhook(payload: bytes, sig: str) -> dict:
    try:
        return stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")
