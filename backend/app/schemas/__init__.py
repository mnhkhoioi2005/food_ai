"""
Schemas package
Export tất cả schemas
"""
from app.schemas.user import (
    UserRegister, UserLogin, Token, TokenData,
    UserPreferences, UserUpdate, UserResponse, 
    UserAdminUpdate, ChangePassword
)
from app.schemas.food import (
    IngredientBase, IngredientCreate, IngredientResponse,
    FoodIngredientResponse, AllergyBase, AllergyCreate, AllergyResponse,
    FoodBase, FoodCreate, FoodUpdate, FoodResponse, FoodDetailResponse,
    FoodListResponse, FoodSearchParams,
    RecognitionResult, RecognitionResponse, RecognitionHistoryResponse
)
from app.schemas.recommendation import (
    RecommendationRequest, RecommendedFood, RecommendationResponse,
    InteractionCreate, InteractionResponse, UserHistoryResponse
)

__all__ = [
    # User
    "UserRegister", "UserLogin", "Token", "TokenData",
    "UserPreferences", "UserUpdate", "UserResponse",
    "UserAdminUpdate", "ChangePassword",
    # Food
    "IngredientBase", "IngredientCreate", "IngredientResponse",
    "FoodIngredientResponse", "AllergyBase", "AllergyCreate", "AllergyResponse",
    "FoodBase", "FoodCreate", "FoodUpdate", "FoodResponse", "FoodDetailResponse",
    "FoodListResponse", "FoodSearchParams",
    "RecognitionResult", "RecognitionResponse", "RecognitionHistoryResponse",
    # Recommendation
    "RecommendationRequest", "RecommendedFood", "RecommendationResponse",
    "InteractionCreate", "InteractionResponse", "UserHistoryResponse"
]
