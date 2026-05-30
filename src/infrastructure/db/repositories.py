from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models import User as DomainUser, Subscription as DomainSubscription
from src.domain.repositories import AbstractUserRepository, AbstractSubscriptionRepository, AbstractAuthRepository

# Auth repository implementation
import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException
from dotenv import load_dotenv
from src.infrastructure.db import orm_models as ORM

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

class SQLAuthRepository(AbstractAuthRepository):
    async def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("sub") is None:
                raise HTTPException(status_code=403, detail="Token is invalid or expired")
            return payload
        except JWTError:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")



def _to_user(orm: ORM.User) -> DomainUser:
    return DomainUser(id=orm.id, username=orm.username,
                      hashed_password=orm.hashed_password, is_premium=orm.is_premium)


def _to_sub(orm: ORM.Subscription) -> DomainSubscription:
    return DomainSubscription(
        id=orm.id, user_id=orm.user_id, status=orm.status,
        started_at=orm.started_at, expires_at=orm.expires_at,
        stripe_customer_id=orm.stripe_customer_id,
        stripe_subscription_id=orm.stripe_subscription_id,
    )


class SQLUserRepository(AbstractUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> DomainUser | None:
        result = await self.db.execute(select(ORM.User).where(ORM.User.username == username))
        orm = result.scalars().first()
        return _to_user(orm) if orm else None

    async def get_by_id(self, user_id: int) -> DomainUser | None:
        orm = await self.db.get(ORM.User, user_id)
        return _to_user(orm) if orm else None

    async def create(self, username: str, hashed_password: str) -> DomainUser:
        orm = ORM.User(username=username, hashed_password=hashed_password)
        self.db.add(orm)
        await self.db.commit()
        await self.db.refresh(orm)
        return _to_user(orm)

    async def get_all(self) -> list[DomainUser]:
        result = await self.db.execute(select(ORM.User))
        return [_to_user(u) for u in result.scalars().all()]

    async def set_premium(self, user_id: int, is_premium: bool) -> None:
        orm = await self.db.get(ORM.User, user_id)
        if orm:
            orm.is_premium = is_premium
            await self.db.commit()


class SQLSubscriptionRepository(AbstractSubscriptionRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> DomainSubscription | None:
        result = await self.db.execute(select(ORM.Subscription).where(ORM.Subscription.user_id == user_id))
        orm = result.scalars().first()
        return _to_sub(orm) if orm else None

    async def get_by_stripe_subscription_id(self, stripe_sub_id: str) -> DomainSubscription | None:
        result = await self.db.execute(
            select(ORM.Subscription).where(ORM.Subscription.stripe_subscription_id == stripe_sub_id)
        )
        orm = result.scalars().first()
        return _to_sub(orm) if orm else None

    async def create(self, user_id: int, status: str, **kwargs) -> DomainSubscription:
        orm = ORM.Subscription(user_id=user_id, status=status, **kwargs)
        self.db.add(orm)
        await self.db.commit()
        await self.db.refresh(orm)
        return _to_sub(orm)

    async def update_status(self, subscription_id: int, status: str) -> None:
        orm = await self.db.get(ORM.Subscription, subscription_id)
        if orm:
            orm.status = status
            await self.db.commit()

    async def get_active_members(self) -> list[tuple[DomainUser, DomainSubscription]]:
        result = await self.db.execute(
            select(ORM.User, ORM.Subscription)
            .join(ORM.Subscription, ORM.Subscription.user_id == ORM.User.id)
            .where(ORM.Subscription.status == "active")
        )
        return [(_to_user(u), _to_sub(s)) for u, s in result.all()]
