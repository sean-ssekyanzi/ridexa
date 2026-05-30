"""
Infrastructure handler layer dataclasses.
These models represent request payloads for the handler layer.
"""


from dataclasses import dataclass, field
from typing import Any


# User schemas moved from infrastructure/schemas/user.py
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    is_premium: bool

    class Config:
        from_attributes = True

class MemberOut(BaseModel):
    username: str
    status: str
    started_at: datetime
    expires_at: datetime | None = None

    class Config:
        from_attributes = True


@dataclass
class UserCredentials:
    username: str
    password: str


@dataclass
class UserIdentity:
    username: str


@dataclass
class SubscriptionActivationData:
    user_id: int
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubscriptionCancelData:
    stripe_subscription_id: str


@dataclass
class PayPalConfirm:
    order_id: str


@dataclass
class MomoRequest:
    phone: str
