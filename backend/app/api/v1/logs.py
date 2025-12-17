"""
Frontend Logs API endpoint for receiving client-side error logs.

This module provides:
- POST /api/logs/frontend - Receive and store frontend error logs
"""
from typing import List, Optional
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.logger import get_logger
from app.settings import get_settings

logger = get_logger(__name__)

router = APIRouter(prefix="/logs", tags=["logs"])


class FrontendLogEntry(BaseModel):
    """Frontend log entry schema."""
    level: str
    message: str
    timestamp: str
    data: Optional[dict] = None
    component: Optional[str] = None
    action: Optional[str] = None
    userAgent: Optional[str] = None
    url: Optional[str] = None
    stack: Optional[str] = None


class FrontendLogsRequest(BaseModel):
    """Request schema for frontend logs."""
    logs: List[FrontendLogEntry]
    timestamp: str


@router.post("/frontend", status_code=status.HTTP_201_CREATED)
async def receive_frontend_logs(request: FrontendLogsRequest):
    """
    Receive frontend error and warning logs.
    
    This endpoint receives logs from the frontend and writes them to:
    1. Backend log files (app.log, error.log)
    2. A dedicated frontend-logs.log file
    """
    try:
        settings = get_settings()
        log_dir = Path(settings.log_dir) if hasattr(settings, 'log_dir') else Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        frontend_log_file = log_dir / "frontend-logs.log"
        
        # Process each log entry
        error_count = 0
        warn_count = 0
        
        for log_entry in request.logs:
            # Format log message
            log_level = log_entry.level.upper()
            timestamp = log_entry.timestamp
            component = log_entry.component or "Unknown"
            action = log_entry.action or "N/A"
            message = log_entry.message
            
            # Build detailed log message
            log_parts = [
                f"[{timestamp}]",
                f"[{log_level}]",
                f"[{component}]",
                f"[{action}]",
                message,
            ]
            
            if log_entry.url:
                log_parts.append(f"URL: {log_entry.url}")
            
            if log_entry.userAgent:
                # Truncate user agent if too long
                ua = log_entry.userAgent[:100] + "..." if len(log_entry.userAgent) > 100 else log_entry.userAgent
                log_parts.append(f"UA: {ua}")
            
            if log_entry.stack:
                log_parts.append(f"\nStack:\n{log_entry.stack}")
            
            if log_entry.data:
                try:
                    import json
                    data_str = json.dumps(log_entry.data, indent=2, default=str)
                    log_parts.append(f"\nData:\n{data_str}")
                except:
                    log_parts.append(f"\nData: {str(log_entry.data)}")
            
            log_message = " | ".join(log_parts)
            
            # Write to dedicated frontend log file
            try:
                with open(frontend_log_file, "a", encoding="utf-8") as f:
                    f.write(log_message + "\n" + "="*80 + "\n")
            except Exception as e:
                logger.warning(f"Failed to write to frontend log file: {e}")
            
            # Also log to backend logger based on level
            if log_entry.level == "error":
                error_count += 1
                logger.error(
                    f"Frontend Error: {message}",
                    extra={
                        "component": component,
                        "action": action,
                        "url": log_entry.url,
                        "user_agent": log_entry.userAgent,
                        "stack": log_entry.stack,
                        "data": log_entry.data,
                    }
                )
            elif log_entry.level == "warn":
                warn_count += 1
                logger.warning(
                    f"Frontend Warning: {message}",
                    extra={
                        "component": component,
                        "action": action,
                        "url": log_entry.url,
                        "data": log_entry.data,
                    }
                )
        
        logger.info(
            f"Received {len(request.logs)} frontend logs: {error_count} errors, {warn_count} warnings"
        )
        
        return {
            "status": "success",
            "received": len(request.logs),
            "errors": error_count,
            "warnings": warn_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Failed to process frontend logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process logs: {str(e)}"
        )

