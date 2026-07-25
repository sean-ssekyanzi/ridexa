"""
Infrastructure handler layer dataclasses.
These models represent request payloads for the handler layer.
"""


from dataclasses import dataclass, field
from typing import Any


# User schemas moved from infrastructure/schemas/user.py

@dataclass
class SubscriptionActivationData:
    user_id: int
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubscriptionCancelData:
    stripe_subscription_id: str

