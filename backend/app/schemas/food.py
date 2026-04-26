"""
Pydantic Schemas cho Food
Request/Response models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== Ingredient Schemas ====================
class IngredientBase(BaseModel):
    """Base schema cho ingredient"""
    name: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    is_allergen: bool = False


class IngredientCreate(IngredientBase):
    """Schema tạo ingredient"""
    pass


class IngredientResponse(IngredientBase):
    """Schema response ingredient"""
    id: int
    
    class Config:
        from_attributes = True


class FoodIngredientResponse(BaseModel):
    """Schema response food ingredient với quantity"""
    ingredient: IngredientResponse
    quantity: Optional[str] = None
    is_main: bool = False
    note: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== Allergy Schemas ====================
class AllergyBase(BaseModel):
    """Base schema cho allergy"""
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = "medium"


class AllergyCreate(AllergyBase):
    """Schema tạo allergy"""
    pass


class AllergyResponse(AllergyBase):
    """Schema response allergy"""
    id: int
    
    class Config:
        from_attributes = True


# ==================== Food Schemas ====================
class FoodBase(BaseModel):
    """Base schema cho food"""
    name: str = Field(..., min_length=1, max_length=255)
    name_en: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    region: Optional[str] = None  # bac, trung, nam
    food_type: Optional[str] = None  # mon_nuoc, mon_kho
    category: Optional[str] = None
    spicy_level: int = Field(0, ge=0, le=5)
    is_vegetarian: bool = False
    is_vegan: bool = False
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    how_to_eat: Optional[str] = None
    how_to_eat_en: Optional[str] = None
    cooking_time: Optional[int] = None
    image_url: Optional[str] = None
    images: List[str] = []
    ai_label: Optional[str] = None


class FoodCreate(FoodBase):
    """Schema tạo food"""
    ingredient_ids: Optional[List[int]] = []
    allergy_ids: Optional[List[int]] = []


class FoodUpdate(BaseModel):
    """Schema cập nhật food"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    region: Optional[str] = None
    food_type: Optional[str] = None
    category: Optional[str] = None
    spicy_level: Optional[int] = Field(None, ge=0, le=5)
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    how_to_eat: Optional[str] = None
    how_to_eat_en: Optional[str] = None
    cooking_time: Optional[int] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    ai_label: Optional[str] = None
    is_active: Optional[bool] = None


class FoodResponse(FoodBase):
    """Schema response food"""
    id: int
    slug: Optional[str] = None
    is_active: bool = True
    view_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FoodDetailResponse(FoodResponse):
    """Schema response food chi tiết"""
    ingredients: List[FoodIngredientResponse] = []
    allergies: List[AllergyResponse] = []
    
    class Config:
        from_attributes = True


class FoodListResponse(BaseModel):
    """Schema response danh sách food"""
    items: List[FoodResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Search/Filter Schemas ====================
class FoodSearchParams(BaseModel):
    """Schema params tìm kiếm food"""
    keyword: Optional[str] = None
    region: Optional[str] = None  # bac, trung, nam
    food_type: Optional[str] = None  # mon_nuoc, mon_kho
    category: Optional[str] = None
    spicy_level_min: Optional[int] = Field(None, ge=0, le=5)
    spicy_level_max: Optional[int] = Field(None, ge=0, le=5)
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    exclude_allergens: Optional[List[str]] = None
    page: int = 1
    page_size: int = 20


# ==================== Recognition Schemas ====================
class RecognitionResult(BaseModel):
    """Schema kết quả nhận diện"""
    food_id: int
    food_name: str
    food_name_en: Optional[str] = None
    confidence: float = Field(..., ge=0, le=1)
    region: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    bbox: Optional[List[float]] = None


class RecognitionResponse(BaseModel):
    """Schema response nhận diện"""
    success: bool
    predictions: List[RecognitionResult]
    top_prediction: Optional[RecognitionResult] = None
    message: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None


class RecognitionHistoryResponse(BaseModel):
    """Schema response lịch sử nhận diện"""
    id: int
    image_url: str
    predicted_food_id: Optional[int] = None
    predicted_food_name: Optional[str] = None
    confidence: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
