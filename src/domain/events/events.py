from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def name(self) -> str:
        return self.__class__.__name__


class AbstractDomainEventDispatcher(ABC):
    """Port for dispatching domain events to infrastructure handlers."""

    @abstractmethod
    async def dispatch(self, event: DomainEvent) -> None: ...


@dataclass
class UserRegisteredEvent(DomainEvent):
    user_id: int
    username: str


@dataclass
class PremiumActivatedEvent(DomainEvent):
    user_id: int
    subscription_id: int
    status: str
    started_at: datetime
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    expires_at: datetime | None = None


@dataclass
class PremiumCancelledEvent(DomainEvent):
    user_id: int
    subscription_id: int
    status: str = "cancelled"
    cancelled_at: datetime = field(default_factory=datetime.utcnow)
    stripe_subscription_id: str | None = None
