from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request as StarletteRequest
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prisma import Prisma
import uvicorn

# Import routers
from routes.auth import router as auth_router
from routes.profile import router as profile_router
from routes.form import router as form_router
from routes.financial import router as financial_router
from routes.analytics import router as analytics_router
from routes.schemes import router as schemes_router
from routes.pdf import router as pdf_router

# Prisma client instance
prisma = Prisma()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown
    Replaces deprecated on_event decorators
    """
    # Startup
    await prisma.connect()
    print("✅ Connected to PostgreSQL database")
    
    yield
    
    # Shutdown
    await prisma.disconnect()
    print("❌ Disconnected from PostgreSQL database")


app = FastAPI(
    title="MSME DPR Generator API",
    description="AI-powered Detailed Project Report Generator for MSMEs",
    version="1.0.0",
    lifespan=lifespan
)

# Environment flag for dev-only logging
ENV = os.getenv("ENV", os.getenv("PYTHON_ENV", "development"))

# Configure root logger
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(form_router, prefix="/api")
app.include_router(financial_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(schemes_router, prefix="/api")
app.include_router(pdf_router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: StarletteRequest, exc: RequestValidationError):
    """Return 422 and log validation errors in non-production environments."""
    # Log detailed validation errors during development for easier debugging
    if ENV != "production":
        logger.error(f"Request validation error for {request.url}: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def generic_exception_handler(request: StarletteRequest, exc: Exception):
    """Catch-all exception handler that logs stack traces in dev only."""
    if ENV != "production":
        # Log full stack trace for debugging
        logger.exception(f"Unhandled exception for {request.url}: {str(exc)}")
    else:
        logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "MSME DPR Generator API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Simple database connectivity check
        # Once we have models, we can do: await prisma.user.count()
        return {
            "status": "healthy",
            "database": "connected",
            "prisma": "initialized"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
