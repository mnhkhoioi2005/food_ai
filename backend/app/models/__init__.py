"""
Models package
Export tất cả các models
"""
from app.models.user import User, RecognitionHistory
from app.models.food import Food, Ingredient, FoodIngredient, Allergy, FoodImage
from app.models.interaction import Interaction, Recommendation, SearchLog

__all__ = [
    "User",
    "RecognitionHistory",
    "Food",
    "Ingredient", 
    "FoodIngredient",
    "Allergy",
    "FoodImage",
    "Interaction",
    "Recommendation",
    "SearchLog"
]
