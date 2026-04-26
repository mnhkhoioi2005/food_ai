"""
Interaction Model - SQLAlchemy
Theo dõi tương tác người dùng với món ăn
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Interaction(Base):
    """Model theo dõi tương tác người dùng"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Loại tương tác: view, like, save, search, recognize, recommend_click
    interaction_type = Column(String(50), nullable=False, index=True)
    
    # Điểm đánh giá (nếu có)
    rating = Column(Integer)  # 1-5 stars
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    food = relationship("Food", back_populates="interactions")


class Recommendation(Base):
    """Model lưu trữ gợi ý đã tạo"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"))
    
    # Loại gợi ý
    recommendation_type = Column(String(50))  # content_based, collaborative, location_based, trending
    
    # Score và lý do
    score = Column(Float)  # Điểm gợi ý (0-1)
    reason = Column(Text)  # Lý do gợi ý
    
    # Vị trí khi gợi ý (nếu location-based)
    latitude = Column(String(50))
    longitude = Column(String(50))
    
    # Trạng thái
    is_clicked = Column(Integer, default=0)  # Đã click vào xem chưa
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SearchLog(Base):
    """Model lưu lịch sử tìm kiếm"""
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Thông tin tìm kiếm
    keyword = Column(String(255), index=True)
    filters = Column(Text)  # JSON string của các filter đã dùng
    results_count = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
