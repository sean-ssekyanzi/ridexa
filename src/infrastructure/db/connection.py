from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.infrastructure.db.orm_models import Base
import os
from dotenv import load_dotenv

load_dotenv()

_RAW_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ridexauser:Ibcco0tE5dvfRqIRNVqLmLMz4LXjbOiC@dpg-d7sva03eo5us73eslfvg-a.oregon-postgres.render.com/ridexa2"
)

# Strip any existing dialect prefix and rebuild with asyncpg
_host = _RAW_URL.split("://", 1)[1]
DB_URL = f"postgresql+asyncpg://{_host}"
if "ssl=" not in DB_URL:
    DB_URL += "?ssl=require"

engine = create_async_engine(DB_URL, echo=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized.")


AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
