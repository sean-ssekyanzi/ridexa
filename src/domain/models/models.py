from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    hashed_password: str
    is_premium: bool = False


@dataclass
class Movie:
    id: int
    title: str
    description: str
    release_year: int
    genre: str
    duration: int  # in minutes
    is_premium: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Subscription:
    id: int
    user_id: int
    status: str
    started_at: datetime
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    expires_at: datetime | None = None
