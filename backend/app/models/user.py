"""
User Model - SQLAlchemy
Quản lý người dùng và preferences
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    
    # Role - phân quyền
    role = Column(String(20), default="user")  # user, admin
    
    # Preferences - sở thích ẩm thực
    spicy_level = Column(Integer, default=2)  # 0-5: không cay đến rất cay
    prefer_soup = Column(Boolean, default=True)  # thích món nước
    is_vegetarian = Column(Boolean, default=False)  # ăn chay
    allergens = Column(JSON, default=[])  # danh sách dị ứng
    favorite_regions = Column(JSON, default=[])  # vùng miền yêu thích: bac, trung, nam
    
    # Location
    latitude = Column(String(50))
    longitude = Column(String(50))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interactions = relationship("Interaction", back_populates="user")
    recognition_history = relationship("RecognitionHistory", back_populates="user")


class RecognitionHistory(Base):
    """Lịch sử nhận diện món ăn"""
    __tablename__ = "recognition_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Có thể null nếu user chưa đăng nhập
    image_url = Column(String(500), nullable=False)
    
    # Kết quả nhận diện
    predicted_food_id = Column(Integer, ForeignKey("foods.id"), nullable=True)
    predicted_food_name = Column(String(255))
    confidence = Column(String(50))  # Độ tin cậy
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recognition_history")
    predicted_food = relationship("Food", foreign_keys=[predicted_food_id])
