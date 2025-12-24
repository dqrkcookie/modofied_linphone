"""
FastAPI application entry point for Linphone Caller.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .api.routes import router
from .core.config import get_settings, ensure_directories, get_log_directory
from .core.linphone_controller import get_controller


# Configure logging
def setup_logging():
    """Setup loguru logging."""
    settings = get_settings()
    log_dir = get_log_directory()
    log_file = log_dir / "app.log"
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL
    )
    
    # Add file handler
    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=settings.LOG_LEVEL
    )
    
    logger.info("Logging configured")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Linphone Caller application")
    
    # Ensure directories exist
    ensure_directories()
    logger.info("Directories verified")
    
    # Check linphone availability
    controller = get_controller()
    available = await controller.check_linphone_available()
    
    if not available:
        logger.warning("Linphone is not available - calls will fail")
    else:
        logger.info("Linphone is available and ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Linphone Caller application")
    
    # End active call if present
    controller = get_controller()
    if controller.has_active_call():
        try:
            logger.info("Terminating active call on shutdown")
            await controller.end_call()
        except Exception as e:
            logger.error(f"Error terminating call: {e}")
    
    logger.info("Application shutdown complete")


# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Linphone Caller API",
    description="HTTP API for automated calling with audio injection using linphone-cli",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "message": "Linphone Caller API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

