"""
Pydantic Schemas cho User
Request/Response models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ==================== Auth Schemas ====================
class UserRegister(BaseModel):
    """Schema đăng ký user"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    """Schema đăng nhập"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema response token"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenData(BaseModel):
    """Data trong token"""
    user_id: Optional[int] = None
    email: Optional[str] = None


# ==================== User Schemas ====================
class UserPreferences(BaseModel):
    """Schema cập nhật preferences"""
    spicy_level: Optional[int] = Field(None, ge=0, le=5)
    prefer_soup: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    allergens: Optional[List[str]] = None
    favorite_regions: Optional[List[str]] = None


class UserUpdate(BaseModel):
    """Schema cập nhật thông tin user"""
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    spicy_level: Optional[int] = Field(None, ge=0, le=5)
    prefer_soup: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    allergens: Optional[List[str]] = None
    favorite_regions: Optional[List[str]] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class UserResponse(BaseModel):
    """Schema response user"""
    id: int
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "user"
    spicy_level: int = 2
    prefer_soup: bool = True
    is_vegetarian: bool = False
    allergens: List[str] = []
    favorite_regions: List[str] = []
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserAdminUpdate(BaseModel):
    """Schema admin cập nhật user"""
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class ChangePassword(BaseModel):
    """Schema đổi mật khẩu"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=50)


# Fix forward reference
Token.model_rebuild()
