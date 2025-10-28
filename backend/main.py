from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prisma import Prisma
import uvicorn

# Import routers
from routes.auth import router as auth_router

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
