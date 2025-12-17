from contextlib import asynccontextmanager
from pathlib import Path
import re
import asyncio
import json
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from .api.v1 import profiles, routes, souvenirs, achievements, logs
from .database import close_db, init_db, get_db
from .models.entities import DemoProfile, Route
from .settings import get_settings
from .llm_logger import get_recent_messages, _llm_messages
from .logger import init_logging_from_settings, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    
    # Initialize logging system
    init_logging_from_settings()
    logger = get_logger(__name__)
    logger.info("🚀 Application starting...")
    
    init_db(settings)
    logger.info("✅ Database initialization completed")
    
    # Seed achievements on startup
    try:
        from app.database import get_db_session
        from app.services.achievement_service import seed_achievements
        logger.info("🌱 Seeding achievement data...")
        async with await get_db_session() as session:
            await seed_achievements(session)
        logger.info("✅ Achievement data seeding completed")
    except Exception as e:
        # Log but don't fail startup if seeding fails
        logger.warning(f"⚠️ Achievement data seeding failed: {e}", exc_info=True)
    
    logger.info("🎉 Application startup completed")
    yield
    
    # Shutdown
    logger.info("🛑 Application shutting down...")
    await close_db()
    logger.info("✅ Database connections closed")


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
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # Explicitly allow OPTIONS
        allow_headers=["*"],  # Allow all headers
        expose_headers=["*"],
    )

    @app.get("/", tags=["info"], response_class=HTMLResponse)
    async def root(db: AsyncSession = Depends(get_db)):
        """Root endpoint with beautiful HTML dashboard."""
        # Get statistics from database
        stats = {}
        try:
            # Count users
            user_count_result = await db.execute(select(func.count(DemoProfile.id)))
            stats["total_users"] = user_count_result.scalar() or 0
            
            # Count routes
            route_count_result = await db.execute(select(func.count(Route.id)))
            stats["total_routes"] = route_count_result.scalar() or 0
            
            # Calculate total XP
            total_xp_result = await db.execute(select(func.sum(DemoProfile.total_xp)))
            stats["total_xp_earned"] = total_xp_result.scalar() or 0
            
            # Get average level
            avg_level_result = await db.execute(select(func.avg(DemoProfile.level)))
            avg_level = avg_level_result.scalar()
            stats["average_level"] = round(float(avg_level), 2) if avg_level else 0.0
        except Exception as e:
            stats = {
                "total_users": 0,
                "total_routes": 0,
                "total_xp_earned": 0,
                "average_level": 0.0,
                "error": str(e)
            }
        
        # Determine database type
        db_type = "SQLite"
        if settings.database_url.startswith("postgresql"):
            db_type = "PostgreSQL"
        
        # Load HTML template
        template_path = Path(__file__).parent / "templates" / "dashboard.html"
        if template_path.exists():
            html_content = template_path.read_text(encoding="utf-8")
        else:
            # Fallback HTML if template not found
            html_content = """
            <!DOCTYPE html>
            <html>
            <head><title>TrailSaga – Hogwarts Expedition Series API</title></head>
            <body>
                <h1>TrailSaga – Hogwarts Expedition Series Backend API</h1>
                <p>Template file not found. Please check templates/dashboard.html</p>
            </body>
            </html>
            """
        
        # Replace template variables
        html_content = html_content.replace("{{ version }}", settings.version)
        html_content = html_content.replace("{{ status }}", "🟢 Operational")
        html_content = html_content.replace("{{ description }}", "Gamified outdoor adventure platform with AI-powered storytelling")
        html_content = html_content.replace("{{ statistics.total_users }}", str(stats.get("total_users", 0)))
        html_content = html_content.replace("{{ statistics.total_routes }}", str(stats.get("total_routes", 0)))
        html_content = html_content.replace("{{ statistics.total_xp_earned }}", str(stats.get("total_xp_earned", 0)))
        html_content = html_content.replace("{{ statistics.average_level }}", str(stats.get("average_level", 0.0)))
        html_content = html_content.replace("{{ database.type }}", db_type)
        html_content = html_content.replace("{{ database.status }}", "✅ Connected")
        html_content = html_content.replace("{{ llm.service }}", "Ollama")
        html_content = html_content.replace("{{ llm.model }}", settings.ollama_model)
        
        return HTMLResponse(content=html_content)

    @app.get("/healthz", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/llm-stream", tags=["monitoring"])
    async def llm_stream():
        """Server-Sent Events endpoint for real-time LLM output streaming."""
        async def event_generator():
            last_count = 0
            while True:
                current_count = len(_llm_messages)
                if current_count > last_count:
                    # New messages available, send them
                    new_messages = list(_llm_messages)[last_count:]
                    for message in new_messages:
                        yield f"data: {message.to_json()}\n\n"
                    last_count = current_count
                else:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                
                await asyncio.sleep(0.5)  # Check every 500ms
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    @app.get("/api/llm-messages", tags=["monitoring"])
    async def get_llm_messages(limit: int = 20):
        """Get recent LLM messages."""
        return {"messages": get_recent_messages(limit)}

    app.include_router(profiles.router, prefix="/api")
    app.include_router(routes.router, prefix="/api")
    app.include_router(souvenirs.router, prefix="/api")
    app.include_router(achievements.router, prefix="/api")
    app.include_router(logs.router, prefix="/api")

    return app


app = create_app()

