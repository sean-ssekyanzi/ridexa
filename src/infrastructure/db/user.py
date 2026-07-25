from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models import User as DomainUser
from src.domain.repositories import AbstractUserRepository

# Auth repository implementation
import os
from dotenv import load_dotenv
from src.infrastructure.db import models as ORM

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

def _to_user(orm: ORM.User) -> DomainUser:
    return DomainUser(id=orm.id, username=orm.username,
                      hashed_password=orm.hashed_password, is_premium=orm.is_premium)


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

