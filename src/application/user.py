from datetime import timedelta
from fastapi import HTTPException
from passlib.context import CryptContext
from src.domain.models import User
from src.domain.ports import UserRepository
from src.infrastructure.db.auth import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def register_user(username: str, password: str, repo: UserRepository) -> User:
    existing = await repo.get_by_username(username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = pwd_context.hash(password)
    return await repo.create(username, hashed)


async def login_user(username: str, password: str, repo: UserRepository) -> str:
    user = await repo.get_by_username(username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    return await create_access_token({"sub": user.username}, timedelta(minutes=30))


async def get_current_user(username: str, repo: UserRepository) -> User:
    user = await repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
