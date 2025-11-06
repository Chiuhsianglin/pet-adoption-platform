from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn

# Import configurations and database
from app.core.config import settings
from app.database import init_db, close_db

# Import API routers
from app.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    print("🚀 Pet Adoption Platform API Starting...")
    
    # Initialize database
    await init_db()
    
    print("✅ Database connection initialized")
    print("🐾 Pet Adoption Platform API Ready!")
    
    yield
    
    # Shutdown
    print("🛑 Pet Adoption Platform API Shutting down...")
    await close_db()
    print("👋 Pet Adoption Platform API Stopped")


# Create FastAPI application
app = FastAPI(
    title="Pet Adoption Platform API",
    description="A comprehensive API for pet adoption management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Pets", "description": "Pet management operations"},
        {"name": "Adoptions", "description": "Adoption application management"},
        {"name": "Authentication", "description": "User authentication and authorization"},
    ],
    lifespan=lifespan
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "🐾 Pet Adoption Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "pet-adoption-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )