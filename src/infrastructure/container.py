from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.user import SQLUserRepository
from src.infrastructure.db.subscription import SQLSubscriptionRepository
from src.infrastructure.db.auth import SQLAuthRepository
from src.infrastructure.events import InMemoryEventDispatcher
from src.application.services.user import UserService
from src.application.services.subscription import SubscriptionService
from src.infrastructure.handlers import Handlers
from src.infrastructure.handlers.user_handlers import UserHandler
from src.infrastructure.handlers.subscription_handler import SubscriptionHandler


class Container(containers.DeclarativeContainer):
    """Global dependency injection container for the application."""

    # Wire handler modules for dependency injection
    wiring_config = containers.WiringConfiguration(modules=Handlers.module())

    # Database session provider - will be overridden per request
    db_session = providers.Dependency(instance_of=AsyncSession)

    # Domain event dispatcher - singleton per container instance
    event_dispatcher = providers.Singleton(InMemoryEventDispatcher)


    # Repository providers
    user_repository = providers.Factory(SQLUserRepository, db_session)
    subscription_repository = providers.Factory(SQLSubscriptionRepository, db_session)
    auth_repository = providers.Singleton(SQLAuthRepository)


    # Service providers
    user_service = providers.Factory(UserService, user_repository, auth_repository, event_dispatcher)
    subscription_service = providers.Factory(SubscriptionService, user_repository, subscription_repository, event_dispatcher)

    # Handler providers
    user_handler = providers.Factory(UserHandler, user_service, event_dispatcher)
    subscription_handler = providers.Factory(SubscriptionHandler, subscription_service, event_dispatcher)
