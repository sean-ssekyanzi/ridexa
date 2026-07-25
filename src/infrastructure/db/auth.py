from datetime import datetime

from src.domain.models import User as DomainUser, Subscription as DomainSubscription
from src.domain.repositories import AbstractAuthRepository

# Auth repository implementation
import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException
from dotenv import load_dotenv
from src.infrastructure.db import models as ORM

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



# def _to_user(orm: ORM.User) -> DomainUser:
#     return DomainUser(id=orm.id, username=orm.username,
#                       hashed_password=orm.hashed_password, is_premium=orm.is_premium)


# def _to_sub(orm: ORM.Subscription) -> DomainSubscription:
#     return DomainSubscription(
#         id=orm.id, user_id=orm.user_id, status=orm.status,
#         started_at=orm.started_at, expires_at=orm.expires_at,
#         stripe_customer_id=orm.stripe_customer_id,
#         stripe_subscription_id=orm.stripe_subscription_id,
#     )

