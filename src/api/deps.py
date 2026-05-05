from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.connection import get_db
from src.infrastructure.db.repositories import SQLUserRepository, SQLSubscriptionRepository
from src.infrastructure.db.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_repo(db: AsyncSession = Depends(get_db)) -> SQLUserRepository:
    return SQLUserRepository(db)


def get_sub_repo(db: AsyncSession = Depends(get_db)) -> SQLSubscriptionRepository:
    return SQLSubscriptionRepository(db)


async def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    return await verify_token(token)
