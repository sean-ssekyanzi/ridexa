from fastapi import APIRouter, Depends
from src.api.deps import get_user_repo, get_current_token_payload
from src.application.user import get_current_user
from src.infrastructure.db.repositories import SQLUserRepository
from src.db.schemas import UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def me(payload: dict = Depends(get_current_token_payload), repo: SQLUserRepository = Depends(get_user_repo)):
    user = await get_current_user(payload["sub"], repo)
    return user


@router.get("/users/")
async def list_users(repo: SQLUserRepository = Depends(get_user_repo)):
    return await repo.get_all()
