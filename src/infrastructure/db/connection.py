import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.infrastructure.db.orm_models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ridexauser:Ibcco0tE5dvfRqIRNVqLmLMz4LXjbOiC@dpg-d7sva03eo5us73eslfvg-a.oregon-postgres.render.com/ridexa2"
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