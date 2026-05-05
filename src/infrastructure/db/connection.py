import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.infrastructure.db.orm_models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ridexauser:niD9d6DMf9P6NLg6lxrYeuC3J7Xjy1hV@dpg-d6pbev2a214c738sbms0-a.oregon-postgres.render.com/ridexa"
)

ssl_ctx = ssl.create_default_context()

engine = create_async_engine(DB_URL, echo=False, connect_args={"ssl": ssl_ctx})


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized.")


AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session