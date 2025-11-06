from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from decouple import config

# Import configurations and database
from app.core.config import settings
from app.database import engine, Base
from app.core.middleware import setup_middleware

# Import API routers
from app.api.v1.auth import router as auth_router
from app.api.v1.pets import router as pets_router
from app.api.v1.adoptions import router as adoptions_router
from app.api.v1.chat import router as chat_router
from app.api.v1.users import router as users_router
from app.api.v1.files import router as files_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    print("🚀 Pet Adoption Platform API Starting...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created/verified")
    print("🐾 Pet Adoption Platform API Ready!")
    
    yield
    
    # Shutdown
    print("🛑 Pet Adoption Platform API Shutting down...")
    await engine.dispose()
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
        {"name": "Chat", "description": "Real-time messaging system"},
        {"name": "Users", "description": "User profile management"},
        {"name": "Files", "description": "File upload and management"},
    ]
)

# Setup middleware
setup_middleware(app)

# Include API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(pets_router, prefix="/api/v1/pets", tags=["Pets"])
app.include_router(adoptions_router, prefix="/api/v1/adoptions", tags=["Adoptions"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(files_router, prefix="/api/v1/files", tags=["Files"])


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