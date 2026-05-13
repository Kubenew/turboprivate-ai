from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from turbo.api.deps import init_app_state, shutdown_app_state
from turbo.api.middleware.rate_limit import RateLimitMiddleware
from turbo.api.middleware.safety_gate import SafetyGateMiddleware
from turbo.api.routes import admin, health, inference, memory, models, safety


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_app_state(app)
    yield
    await shutdown_app_state(app)


def create_app() -> FastAPI:
    app = FastAPI(
        title="TurboPrivate AI",
        version="0.1.3",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
    app.add_middleware(SafetyGateMiddleware)

    app.include_router(health.router, tags=["health"])
    app.include_router(inference.router, prefix="/v1", tags=["inference"])
    app.include_router(safety.router, prefix="/api/v1", tags=["safety"])
    app.include_router(models.router, prefix="/api/v1", tags=["models"])
    app.include_router(memory.router, prefix="/api/v1", tags=["memory"])
    app.include_router(admin.router, prefix="/api/v1", tags=["admin"])

    return app


app = create_app()
