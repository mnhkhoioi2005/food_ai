"""
FastAPI Backend - Vietnamese Food AI Recognition System
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, engine

# Tạo tất cả tables trong database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vietnamese Food AI API",
    description="""
    API nhận diện và gợi ý món ăn Việt Nam bằng AI.
    
    ## Tính năng chính:
    * **Nhận diện món ăn** - Upload ảnh hoặc chụp camera để AI nhận diện
    * **Tìm kiếm** - Tìm món ăn theo tên, vùng miền, nguyên liệu
    * **Gợi ý thông minh** - Gợi ý dựa trên khẩu vị và lịch sử
    * **Quản lý Admin** - CRUD món ăn, người dùng, thống kê
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (uploads)
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vietnamese Food AI Recognition API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vietfood-api"
    }
