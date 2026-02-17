"""KiraAI FastAPI Application"""

from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.database import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.app_name} API...")
    print(f"📍 Environment: {settings.app_env}")
    print(f"🔧 Debug mode: {settings.debug}")

    # Redis connection test
    try:
        redis_client.ping()
        print("✅ Redis connection: OK")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

    yield

    # Shutdown
    print(f"🛑 Shutting down {settings.app_name} API...")
    try:
        redis_client.close()
    except Exception as e:
        print(f"Error closing Redis: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI転職支援プラットフォーム - Backend API",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods.split(","),
    allow_headers=settings.cors_allow_headers.split(","),
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    return response


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for Docker health check

    Returns:
        dict: Health status and component checks
    """
    health_status = {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": "0.1.0",
        "environment": settings.app_env,
        "components": {
            "api": "ok",
            "redis": "unknown",
            "database": "unknown",
        }
    }

    # Redis health check
    try:
        redis_client.ping()
        health_status["components"]["redis"] = "ok"
    except Exception as e:
        health_status["components"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Database health check
    try:
        from app.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["components"]["database"] = "ok"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@app.get("/", tags=["System"])
async def root() -> Dict[str, str]:
    """Root endpoint

    Returns:
        dict: Welcome message
    """
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": "/docs",
        "health": "/health",
    }


# API routes
from app.routers.auth import router as auth_router
from app.routers.hearing import router as hearing_router
from app.routers.documents import router as documents_router
from app.routers.jobs import router as jobs_router
from app.routers.applications import router as applications_router
from app.routers.agent import router as agent_router
from app.routers.learning_data import router as learning_data_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(hearing_router, prefix="/api/hearing", tags=["AI Hearing"])
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(agent_router)
app.include_router(learning_data_router)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "path": str(request.url),
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
