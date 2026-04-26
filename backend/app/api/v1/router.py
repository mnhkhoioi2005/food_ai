"""
API Router - combine all endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, food_recognition, food_search, recommendation, user, location, chat

api_router = APIRouter()

# Authentication
api_router.include_router(
    auth.router,
    tags=["Authentication"]
)

# Food Recognition
api_router.include_router(
    food_recognition.router, 
    prefix="/recognition", 
    tags=["Food Recognition"]
)

# Food Search & CRUD
api_router.include_router(
    food_search.router, 
    prefix="/foods", 
    tags=["Foods"]
)

# Recommendations
api_router.include_router(
    recommendation.router, 
    prefix="/recommendations", 
    tags=["Recommendations"]
)

# User Management
api_router.include_router(
    user.router, 
    prefix="/users", 
    tags=["Users"]
)

# Location
api_router.include_router(
    location.router, 
    prefix="/location", 
    tags=["Location"]
)

# AI Chat Assistant
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["AI Chat"]
)
