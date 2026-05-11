from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.infrastructure.db.orm_models import Base

DB_URL = "postgresql+asyncpg://ridexauser:Ibcco0tE5dvfRqIRNVqLmLMz4LXjbOiC@dpg-d7sva03eo5us73eslfvg-a.oregon-postgres.render.com/ridexa2?ssl=require"

engine = create_async_engine(DB_URL, echo=False)


async def init_db():
    # Tables managed by Alembic migrations — skip create_all
    print("Database ready.")


AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
