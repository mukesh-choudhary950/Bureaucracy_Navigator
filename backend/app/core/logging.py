import logging
import sys
import os
from loguru import logger
from app.core.config import settings


class InterceptHandler(logging.Handler):
    """Intercept standard logging and forward it to Loguru"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """Setup application logging"""

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Remove default handlers
    logger.remove()

    # Console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # Error log file
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} - {message}",
        level="ERROR",
        backtrace=True,
        diagnose=True
    )

    # Full log file
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        backtrace=True,
        diagnose=True
    )

    # Redirect standard logging to Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Redirect library logs
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("fastapi").handlers = [InterceptHandler()]
    logging.getLogger("sqlalchemy").handlers = [InterceptHandler()]
    logging.getLogger("sqlalchemy.engine").handlers = [InterceptHandler()]
    logging.getLogger("chromadb").handlers = [InterceptHandler()]

    return logger


# Initialize logging
app_logger = setup_logging()


def get_logger(name: str = None):
    """Get logger instance"""
    if name:
        return logger.bind(name=name)
    return logger