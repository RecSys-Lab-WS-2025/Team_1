from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import sample
from .database import close_db, init_db
from .settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    init_db(settings)
    yield
    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    """
    Application factory that configures FastAPI along with shared dependencies.
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js default dev port
            "http://localhost:3001",  # Alternative port
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

    @app.get("/healthz", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(sample.router, prefix="/api")

    return app


app = create_app()

