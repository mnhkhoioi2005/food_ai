"""
Food Model - SQLAlchemy
Quản lý món ăn và nguyên liệu
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, JSON, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# Association table for Food-Allergy (many-to-many)
food_allergies = Table(
    'food_allergies',
    Base.metadata,
    Column('food_id', Integer, ForeignKey('foods.id'), primary_key=True),
    Column('allergy_id', Integer, ForeignKey('allergies.id'), primary_key=True)
)


class Food(Base):
    """Model món ăn Việt Nam"""
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    
    # Thông tin cơ bản - đa ngôn ngữ
    name = Column(String(255), nullable=False, index=True)  # Tên tiếng Việt
    name_en = Column(String(255))  # Tên tiếng Anh
    slug = Column(String(255), unique=True, index=True)  # URL-friendly name
    
    description = Column(Text)  # Mô tả tiếng Việt
    description_en = Column(Text)  # Mô tả tiếng Anh
    
    # Phân loại
    region = Column(String(50), index=True)  # bac, trung, nam
    food_type = Column(String(50), index=True)  # mon_nuoc, mon_kho, do_uong, trang_mieng
    category = Column(String(100))  # Phở, Bún, Cơm, Bánh, etc.
    
    # Đặc điểm khẩu vị
    spicy_level = Column(Integer, default=0)  # 0-5
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    
    # Thông tin dinh dưỡng (per serving)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    fiber = Column(Float)
    
    # Hướng dẫn
    how_to_eat = Column(Text)  # Cách ăn đúng chuẩn
    how_to_eat_en = Column(Text)
    cooking_time = Column(Integer)  # Thời gian nấu (phút)
    
    # Hình ảnh
    image_url = Column(String(500))  # Ảnh chính
    images = Column(JSON, default=[])  # Danh sách ảnh phụ
    
    # AI label - để training model
    ai_label = Column(String(100), index=True)
    
    # Trạng thái
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ingredients = relationship("FoodIngredient", back_populates="food", cascade="all, delete-orphan")
    allergies = relationship("Allergy", secondary=food_allergies, back_populates="foods")
    interactions = relationship("Interaction", back_populates="food")


class Ingredient(Base):
    """Model nguyên liệu"""
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    name_en = Column(String(255))
    category = Column(String(100))  # Thịt, Rau, Gia vị, etc.
    is_allergen = Column(Boolean, default=False)  # Có phải chất gây dị ứng không
    
    # Relationships
    foods = relationship("FoodIngredient", back_populates="ingredient")


class FoodIngredient(Base):
    """Association table cho Food-Ingredient với thông tin thêm"""
    __tablename__ = "food_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantity = Column(String(100))  # Số lượng: "200g", "2 muỗng canh", etc.
    is_main = Column(Boolean, default=False)  # Nguyên liệu chính
    note = Column(String(255))  # Ghi chú thêm
    
    food = relationship("Food", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="foods")


class Allergy(Base):
    """Model thông tin dị ứng"""
    __tablename__ = "allergies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # Gluten, Đậu phộng, etc.
    name_en = Column(String(100))
    description = Column(Text)
    severity = Column(String(20))  # low, medium, high
    
    # Relationships
    foods = relationship("Food", secondary=food_allergies, back_populates="allergies")


class FoodImage(Base):
    """Model quản lý hình ảnh training"""
    __tablename__ = "food_images"
    
    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"))
    image_url = Column(String(500), nullable=False)
    is_training = Column(Boolean, default=True)  # Dùng cho training model
    source = Column(String(100))  # Nguồn: upload, kaggle, roboflow
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
