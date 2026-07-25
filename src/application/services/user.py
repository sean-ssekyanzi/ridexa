from datetime import timedelta
from src.domain.models import User
from src.domain.repositories import AbstractUserRepository
from src.domain.use_cases.user import AbstractUserService
from src.domain.events.events import UserRegisteredEvent, AbstractDomainEventDispatcher
from src.domain.models.exceptions import UserAlreadyExistsError, UserNotFoundError, InvalidCredentialsError
from src.domain.repositories.auth import AbstractAuthRepository 
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




class UserService(AbstractUserService):
    def __init__(self, repo: AbstractUserRepository, auth_repo:AbstractAuthRepository, event_dispatcher: AbstractDomainEventDispatcher | None = None):
        self._repo = repo
        self._auth_repo = auth_repo
        self._event_dispatcher = event_dispatcher

    async def register(self, username: str, password: str) -> User:
        if await self._repo.get_by_username(username):
            raise UserAlreadyExistsError(f"Username '{username}' is already taken")
        user = await self._repo.create(username, pwd_context.hash(password))
        if self._event_dispatcher:
            event = UserRegisteredEvent(user_id=user.id, username=user.username)
            await self._event_dispatcher.dispatch(event)
        return user

    async def login(self, username: str, password: str) -> str:
        user = await self._repo.get_by_username(username)
        if not user or not pwd_context.verify(password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect username or password")
        return await self._auth_repo.create_access_token({"sub": user.username}, timedelta(minutes=30))

    async def get_current_user(self, username: str) -> User:
        user = await self._repo.get_by_username(username)
        if not user:
            raise UserNotFoundError(f"User '{username}' not found")
        return user

    async def list_users(self) -> list[User]:
        return await self._repo.get_all()

    # Domain use-case implementations
    # async def register_user(self, username: str, password: str, repo: AbstractUserRepository) -> User:
    #     if await repo.get_by_username(username):
    #         raise UserAlreadyExistsError(f"Username '{username}' is already taken")
    #     return await repo.create(username, pwd_context.hash(password))

    # async def authenticate_user(self, username: str, password: str, repo: AbstractUserRepository) -> User:
    #     user = await repo.get_by_username(username)
    #     if not user or not pwd_context.verify(password, user.hashed_password):
    #         raise InvalidCredentialsError("Incorrect username or password")
    #     return user

    # async def get_user(self, username: str, repo: AbstractUserRepository) -> User:
    #     user = await repo.get_by_username(username)
    #     if not user:
    #         raise UserNotFoundError(f"User '{username}' not found")
    #     return user
