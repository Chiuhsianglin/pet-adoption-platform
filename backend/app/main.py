from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path

# Import configurations and database
from app.core.config import settings
from app.database import init_db, close_db

# V2 API Router- 三層架構：Controller -> Service -> Repository
from app.api.v2 import api_router as v2_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Pet Adoption API...")
    await init_db()
    yield
    await close_db()
    print("👋 API shutdown complete.")

app = FastAPI(
    title="Pet Adoption Platform API",
    version="2.0.0",
    docs_url="/api/v2/docs",
    redoc_url="/api/v2/redoc",
    openapi_url="/api/v2/openapi.json",
    lifespan=lifespan,
)

# ✅ Allow frontend access (Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ V2 API (新架構：Controller -> Service -> Repository)
# 所有 API 端點統一使用 /api/v2 前綴
app.include_router(v2_router, prefix="/api/v2")

# Mount static files for uploaded content
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

@app.get("/")
async def root():
    return {"message": "Pet Adoption API is running", "docs": "/api/v1/docs"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
@app.get("/")
async def root():
    return {
        "message": "Pet Adoption API V2 is running",
        "version": "2.0.0",
        "docs": "/api/v2/docs",
        "architecture": "Three-Layer (Controller -> Service -> Repository)"
    }