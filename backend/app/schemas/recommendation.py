"""
Pydantic Schemas cho Recommendation
Request/Response models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RecommendationRequest(BaseModel):
    """Schema request gợi ý món ăn"""
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)
    include_types: Optional[List[str]] = None  # content_based, collaborative, location_based


class RecommendedFood(BaseModel):
    """Schema món ăn được gợi ý"""
    id: int
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None
    food_type: Optional[str] = None
    spicy_level: int = 0
    is_vegetarian: bool = False
    image_url: Optional[str] = None
    
    # Thông tin gợi ý
    score: float = Field(..., ge=0, le=1)
    recommendation_type: str  # content_based, collaborative, location_based, trending
    reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Schema response gợi ý"""
    success: bool
    recommendations: List[RecommendedFood]
    total: int
    message: Optional[str] = None


class InteractionCreate(BaseModel):
    """Schema tạo interaction"""
    food_id: int
    interaction_type: str = Field(..., pattern="^(view|like|save|search|recognize|recommend_click)$")
    rating: Optional[int] = Field(None, ge=1, le=5)


class InteractionResponse(BaseModel):
    """Schema response interaction"""
    id: int
    user_id: int
    food_id: int
    interaction_type: str
    rating: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserHistoryResponse(BaseModel):
    """Schema response lịch sử user"""
    interactions: List[InteractionResponse]
    total: int
    
    class Config:
        from_attributes = True
