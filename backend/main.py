from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.database import prisma
from app.config import settings
from app.routers import auth, users, dpr, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    await prisma.connect()
    print("✅ Database connected successfully")
    print("🚀 MSME DPR Generator API Started")
    yield
    # Shutdown
    await prisma.disconnect()
    print("❌ Database disconnected")
    print("👋 MSME DPR Generator API Stopped")


# Create FastAPI app
app = FastAPI(
    title="MSME DPR Generator API",
    description="AI-Powered Detailed Project Report Generator for MSMEs",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(dpr.router, prefix="/api/dpr", tags=["DPR"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    return {
        "message": "MSME DPR Generator API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
