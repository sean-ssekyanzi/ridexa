from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.db.connection import init_db
from src.infrastructure.fast_api import create_app


@asynccontextmanager
async def lifespan(app):
    print("server is starting")
    await init_db()
    yield
    print("server is stopping")


app = create_app(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ridexa-frntend.onrender.com",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"message": "Hello World"}
