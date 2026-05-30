from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.infrastructure.handlers.models import UserCredentials
from src.infrastructure.auth import get_current_token_payload
from src.infrastructure.di import get_service_container
from src.infrastructure.container import Container
from src.infrastructure.schemas.user import UserCreate, UserOut
from src.application.services.user import UserService

router = APIRouter(tags=["auth", "users"])


@router.post("/register")
@inject
async def register(
    user: UserCreate,
    user_service: UserService = Depends(Provide[Container.user_service]),
    container: Container = Depends(get_service_container)
):
    return await user_service.register(user.username, user.password)


@router.post("/token")
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(Provide[Container.user_service]),
    container: Container = Depends(get_service_container)
):
    token = await user_service.login(form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
@inject
async def me(
    payload: dict = Depends(get_current_token_payload),
    user_service: UserService = Depends(Provide[Container.user_service]),
    container: Container = Depends(get_service_container)
):
    return await user_service.get_current_user(payload["sub"])


@router.get("/users/", response_model=list[UserOut])
@inject
async def list_users(
    user_service: UserService = Depends(Provide[Container.user_service]),
    container: Container = Depends(get_service_container)
):
    return await user_service.list_users()
