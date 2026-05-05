from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy import text
from src.config import CONFIG
from src.db.models import Base
from sqlalchemy.orm import sessionmaker

#db url
DB_URL = "postgresql://ridexauser:Ibcco0tE5dvfRqIRNVqLmLMz4LXjbOiC@dpg-d7sva03eo5us73eslfvg-a.oregon-postgres.render.com/ridexa2"


engine = create_async_engine(
    url=DB_URL,
    echo=True,
)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized and tables created if they didn't already exist.")


AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session