from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.infrastructure.handlers.models import UserCredentials
from src.infrastructure.auth import get_current_token_payload
from src.infrastructure.di import get_service_container
from src.infrastructure.container import Container
from src.infrastructure.schemas.user import UserCreate, UserOut
from src.application.services.user import UserService
from src.domain.exceptions import UserAlreadyExistsError, UserNotFoundError, InvalidCredentialsError
from fastapi import HTTPException

router = APIRouter(tags=["auth", "users"])



@router.post("/register")
@inject
async def register(
    user: UserCreate,
    user_service: UserService = Depends(Provide[Container.user_service]),
    container: Container = Depends(get_service_container)
):
    try:
        return await user_service.register(user.username, user.password)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/token")
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(Provide[Container.user_service]),
    container: Container = Depends(get_service_container)
):
    try:
        token = await user_service.login(form_data.username, form_data.password)
        return {"access_token": token, "token_type": "bearer"}
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e), headers={"WWW-Authenticate": "Bearer"})



@router.get("/me", response_model=UserOut)
@inject
async def me(
    payload: dict = Depends(get_current_token_payload),
    user_service: UserService = Depends(Provide[Container.user_service]),
    container: Container = Depends(get_service_container)
):
    try:
        return await user_service.get_current_user(payload["sub"])
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/users/", response_model=list[UserOut])
@inject
async def list_users(
    user_service: UserService = Depends(Provide[Container.user_service]),
    container: Container = Depends(get_service_container)
):
    return await user_service.list_users()
