"""
Centralized logging configuration module.

Provides a structured logging system for the entire application with:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console outputs
- Structured log formats
- Request tracing
- Performance monitoring

Usage:
    from app.logger import get_logger
    
    logger = get_logger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message", exc_info=True)
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime

from app.settings import get_settings


# Log formats
DETAILED_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)
SIMPLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"

# Log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log files
APP_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
DEBUG_LOG_FILE = LOG_DIR / "debug.log"


def setup_logging(
    log_level: str = "INFO",
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    detailed_format: bool = True
) -> None:
    """
    Configure application-wide logging.
    
    Parameters
    ----------
    log_level : str
        Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    enable_file_logging : bool
        Whether to enable file logging
    enable_console_logging : bool
        Whether to enable console logging
    detailed_format : bool
        Whether to use detailed format (including function name and line number)
    """
    # Convert log level string to numeric level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Choose format
    log_format = DETAILED_FORMAT if detailed_format else SIMPLE_FORMAT
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file_logging:
        # Application log (all levels)
        app_handler = RotatingFileHandler(
            APP_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        app_handler.setLevel(logging.DEBUG)  # Log all levels to application file
        app_formatter = logging.Formatter(log_format, date_format)
        app_handler.setFormatter(app_formatter)
        root_logger.addHandler(app_handler)
        
        # Error log (WARNING and above)
        error_handler = RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.WARNING)
        error_formatter = logging.Formatter(log_format, date_format)
        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)
        
        # Debug log (DEBUG only)
        debug_handler = RotatingFileHandler(
            DEBUG_LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8"
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter(log_format, date_format)
        debug_handler.setFormatter(debug_formatter)
        root_logger.addHandler(debug_handler)
    
    # Configure third-party logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Log logging system initialization
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"File logging: {'enabled' if enable_file_logging else 'disabled'}")
    logger.info(f"Console logging: {'enabled' if enable_console_logging else 'disabled'}")
    logger.info(f"Log directory: {LOG_DIR}")
    logger.info("=" * 80)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Parameters
    ----------
    name : Optional[str]
        Logger name, usually __name__
    
    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    return logging.getLogger(name or __name__)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    user_id: Optional[int] = None,
    **kwargs
) -> None:
    """
    Log detailed information about an HTTP request.
    
    Parameters
    ----------
    logger : logging.Logger
        Logger instance
    method : str
        HTTP method
    path : str
        Request path
    status_code : Optional[int]
        Response status code
    duration_ms : Optional[float]
        Request processing time in milliseconds
    user_id : Optional[int]
        User ID
    **kwargs
        Additional information to log
    """
    parts = [f"{method} {path}"]
    
    if status_code:
        parts.append(f"status={status_code}")
    
    if duration_ms is not None:
        parts.append(f"duration={duration_ms:.2f}ms")
    
    if user_id:
        parts.append(f"user_id={user_id}")
    
    if kwargs:
        extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extra_info)
    
    message = " | ".join(parts)
    logger.info(f"🌐 {message}")


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    record_id: Optional[int] = None,
    duration_ms: Optional[float] = None,
    **kwargs
) -> None:
    """
    Log detailed information about a database operation.
    
    Parameters
    ----------
    logger : logging.Logger
        Logger instance
    operation : str
        Operation type (SELECT, INSERT, UPDATE, DELETE)
    table : str
        Table name
    record_id : Optional[int]
        Record ID
    duration_ms : Optional[float]
        Operation duration in milliseconds
    **kwargs
        Additional information to log
    """
    parts = [f"{operation} {table}"]
    
    if record_id:
        parts.append(f"id={record_id}")
    
    if duration_ms is not None:
        parts.append(f"duration={duration_ms:.2f}ms")
    
    if kwargs:
        extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extra_info)
    
    message = " | ".join(parts)
    logger.debug(f"💾 {message}")


def log_api_call(
    logger: logging.Logger,
    service: str,
    endpoint: str,
    method: str = "POST",
    duration_ms: Optional[float] = None,
    success: bool = True,
    **kwargs
) -> None:
    """
    Log detailed information about an external API call.
    
    Parameters
    ----------
    logger : logging.Logger
        Logger instance
    service : str
        Service name (e.g., "Ollama", "OutdoorActive")
    endpoint : str
        API endpoint
    method : str
        HTTP method
    duration_ms : Optional[float]
        Call duration in milliseconds
    success : bool
        Whether the call was successful
    **kwargs
        Additional information to log
    """
    status = "✅" if success else "❌"
    parts = [f"{status} {service} {method} {endpoint}"]
    
    if duration_ms is not None:
        parts.append(f"duration={duration_ms:.2f}ms")
    
    if kwargs:
        extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extra_info)
    
    message = " | ".join(parts)
    level = logging.INFO if success else logging.ERROR
    logger.log(level, f"🔌 {message}")


def log_business_logic(
    logger: logging.Logger,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    **kwargs
) -> None:
    """
    Log detailed information about business logic operations.
    
    Parameters
    ----------
    logger : logging.Logger
        Logger instance
    action : str
        Operation description (e.g., "created", "updated", "calculated")
    entity_type : str
        Entity type (e.g., "Profile", "Route", "Souvenir")
    entity_id : Optional[int]
        Entity ID
    **kwargs
        Additional information to log
    """
    parts = [f"{action} {entity_type}"]
    
    if entity_id:
        parts.append(f"id={entity_id}")
    
    if kwargs:
        extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extra_info)
    
    message = " | ".join(parts)
    logger.info(f"📋 {message}")


# Initialize logging system automatically from settings
def init_logging_from_settings() -> None:
    """Initialize logging system from application settings."""
    settings = get_settings()
    
    # Read logging configuration from environment variables or settings
    log_level = getattr(settings, "log_level", "INFO")
    enable_file = getattr(settings, "log_enable_file", True)
    enable_console = getattr(settings, "log_enable_console", True)
    detailed_format = getattr(settings, "log_detailed_format", True)
    
    setup_logging(
        log_level=log_level,
        enable_file_logging=enable_file,
        enable_console_logging=enable_console,
        detailed_format=detailed_format
    )

