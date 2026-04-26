"""
Ingredient Model - SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    name_en = Column(String(255))
    category = Column(String(100))  # meat, vegetable, spice, etc.
    is_allergen = Column(Boolean, default=False)
    allergen_type = Column(String(100))  # gluten, dairy, shellfish, etc.
    
    foods = relationship("FoodIngredient", back_populates="ingredient")
