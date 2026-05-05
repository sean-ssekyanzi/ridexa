from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.api.deps import get_user_repo
from src.application.user import register_user, login_user
from src.infrastructure.db.repositories import SQLUserRepository
from src.db.schemas import UserCreate, UserOut

router = APIRouter()


@router.post("/register")
async def register(user: UserCreate, repo: SQLUserRepository = Depends(get_user_repo)):
    return await register_user(user.username, user.password, repo)


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), repo: SQLUserRepository = Depends(get_user_repo)):
    token = await login_user(form_data.username, form_data.password, repo)
    return {"access_token": token, "token_type": "bearer"}
