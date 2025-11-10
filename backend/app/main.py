from fastapi import FastAPI

from .api.v1 import sample
from .settings import get_settings
from .supabase import get_supabase_client


def create_app() -> FastAPI:
    """
    Application factory that configures FastAPI along with shared dependencies.
    """
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version)

    @app.get("/healthz", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.on_event("startup")
    async def on_startup() -> None:
        # Trigger Supabase client instantiation to fail fast if misconfigured.
        get_supabase_client(settings)

    app.include_router(sample.router, prefix="/api/v1")

    return app


app = create_app()

