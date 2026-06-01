from fastapi import FastAPI
from src.infrastructure.handlers import Handlers
from src.infrastructure.container import Container


def create_app(lifespan=None) -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    # Wire the dependency injection container globally
    container = Container()
    container.wire()

    for handler in Handlers.iterator():
        if hasattr(handler, "router"):
            app.include_router(handler.router)
    return app
