"""
Infrastructure dependency providers.
This module provides request-scoped database sessions for dependency injection.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.connection import get_db
from src.infrastructure.container import Container


async def get_service_container(db: AsyncSession = Depends(get_db)) -> Container:
    """Get a container instance with the current request's database session."""
    container = Container()
    container.db_session.override(db)
    return container
