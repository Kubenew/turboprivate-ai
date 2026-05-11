from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from turbo.api.deps import init_app_state, shutdown_app_state
from turbo.api.routes import admin, health, inference, memory, models, safety


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_app_state(app)
    yield
    await shutdown_app_state(app)


def create_app() -> FastAPI:
    app = FastAPI(
        title="TurboPrivate AI",
        version="0.1.2",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(inference.router, prefix="/v1", tags=["inference"])
    app.include_router(safety.router, prefix="/api/v1", tags=["safety"])
    app.include_router(models.router, prefix="/api/v1", tags=["models"])
    app.include_router(memory.router, prefix="/api/v1", tags=["memory"])
    app.include_router(admin.router, prefix="/api/v1", tags=["admin"])

    return app


app = create_app()
